# Cleaning a Dataset with Pandas in 10 Minutes

When you first open a dataset, you want to jump straight into building a model. I used to do the same. Then one day I noticed that "İstanbul", "istanbul" and "İstanbul " (with a trailing space) were being counted as three separate cities, and I finally understood why my chart looked so strange. Since then, I start every project with cleaning.

The steps below are what I apply, in order, to every new dataset. They all use Pandas, and the whole thing takes about 10 minutes from start to finish.

## Sample data

Let's work with a small orders table. To mimic the mess of real life, I deliberately put a few problems in it.

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Sipariş No": [1001, 1002, 1003, 1003, 1004, 1005, 1006],
    "Müşteri Adı ": ["Ayşe Kaya", "mehmet demir", "Zeynep  Arslan", "Zeynep  Arslan", None, "Can Yıldız", "ELİF ŞAHİN"],
    "Şehir": ["İzmir", "izmir", "Ankara ", "Ankara ", "İstanbul", "istanbul", "Bursa"],
    "Tutar": ["250", "1.200", "89,90", "89,90", "430", None, "99999"],
    "Tarih": ["2026-01-05", "05.01.2026", "2026-01-07", "2026-01-07", "2026-01-09", "2026-01-10", "2026-01-11"],
})
```

The column names are in Turkish: `Sipariş No` is the order number, `Müşteri Adı` the customer name, `Şehir` the city, `Tutar` the amount and `Tarih` the date. I've left them as they are so the code runs exactly as written.

## 1. Look first, touch later

Before you start cleaning, you need to see what the data looks like. These three lines usually give me a good enough idea:

```python
df.info()
df.isna().sum()
df.describe(include="all")
```

`info()` shows which column has which type. If you see that the `Tutar` and `Tarih` columns come out as `object` (in other words, text), you have a problem. Numbers stored as text will let you down the moment you try to take an average.

## 2. Fix the column names

In the table above, the ` Müşteri Adı  ` column has an invisible space at the end. Things like this show up as a `KeyError` when you type `df["Müşteri Adı"]`, and tracking down the cause is annoying.

```python
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
      .str.replace("ı", "i")
      .str.replace("ş", "s")
      .str.replace("ö", "o")
)
```

The result is names like `siparis_no`, `musteri_adi`, `sehir`, `tutar` and `tarih`, which can be typed anywhere without trouble. Removing Turkish characters from column names is a matter of habit, but it saves you from a lot of pointless errors while coding.

## 3. Remove duplicate rows

Order 1003 appears twice in the table. First check how many there are, then drop them:

```python
df.duplicated().sum()   # 1

df = df.drop_duplicates()
```

If you want to deduplicate based on a specific column, you can use `subset`:

```python
df = df.drop_duplicates(subset="siparis_no", keep="first")
```

## 4. Standardize text columns

This is the part that takes the most time and makes the biggest difference. We clean up the whitespace and make capitalization consistent.

```python
df["musteri_adi"] = df["musteri_adi"].str.strip().str.replace(r"\s+", " ", regex=True).str.title()
df["sehir"] = df["sehir"].str.strip().str.title()
```

A warning: Python's `lower()` and `title()` behave strangely with the Turkish letters `İ` and `ı`. `"İZMİR".lower()` gives you `"i̇zmi̇r"`, with an invisible dot slipped in. If the data matters to you, map those letters by hand first:

```python
def tr_lower(s):
    return s.replace("İ", "i").replace("I", "ı").lower()

df["sehir"] = df["sehir"].map(lambda x: tr_lower(x).title() if isinstance(x, str) else x)
```

If there are a lot of spelling variations (like "Istanbul" or "İstnbul"), the most reliable method is to look at `df["sehir"].value_counts()` and fix them with a dictionary:

```python
duzeltme = {"Istanbul": "İstanbul", "Izmir": "İzmir"}
df["sehir"] = df["sehir"].replace(duzeltme)
```

## 5. Fix the data types

The `Tutar` column contains both "1.200" (the Turkish thousands separator) and "89,90" (a decimal comma). First these need to be converted into a format Python understands:

```python
df["tutar"] = (
    df["tutar"]
      .str.replace(".", "", regex=False)    # drop the thousands separator
      .str.replace(",", ".", regex=False)   # turn the comma into a decimal point
)
df["tutar"] = pd.to_numeric(df["tutar"], errors="coerce")
```

`errors="coerce"` turns values that can't be converted into `NaN` instead of raising an error. That way you can count afterwards how many were broken.

The dates also come in two different formats. With Pandas 2.x you can solve it like this:

```python
df["tarih"] = pd.to_datetime(df["tarih"], format="mixed", dayfirst=True, errors="coerce")
```

`dayfirst=True` matters, because "05.01.2026" means January 5th in Turkey, but the default setting may read it as May 1st. This mistake happens silently, and it can take weeks to notice.

## 6. What will you do about missing values?

There's no single right answer to this one. It depends on the situation.

```python
df.isna().sum()
```

- **Dropping the row:** Reasonable when few values are missing and that row is critical for the analysis. `df.dropna(subset=["tutar"])`
- **Filling with a fixed value:** Works for categorical columns. `df["musteri_adi"].fillna("Bilinmiyor")` ("Bilinmiyor" means "Unknown")
- **Filling with the mean or median:** Used for numeric columns. If there are outliers, the median is safer. `df["tutar"].fillna(df["tutar"].median())`

My rule is this: before you fill anything, think about why it's missing. If the gaps aren't random, say a particular branch never enters an amount, then filling with the mean paints a misleading picture.

## 7. Check for outliers

There's an order for 99999 TL in the table. It might be real, but it's most likely a data entry error. Take a look before you delete anything:

```python
q1 = df["tutar"].quantile(0.25)
q3 = df["tutar"].quantile(0.75)
iqr = q3 - q1

alt, ust = q1 - 1.5 * iqr, q3 + 1.5 * iqr   # lower and upper bounds
aykiri = df[(df["tutar"] < alt) | (df["tutar"] > ust)]
print(aykiri)
```

This method lists the suspicious rows, but the decision is yours. Don't automatically delete a value just because it's an outlier. Ask its source first: is this a real corporate order, or a few extra zeros typed by accident?

## Put it all in one function

To avoid rewriting the same steps from scratch in every project, I keep them in a function:

```python
def temizle(df):
    df = df.copy()

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.drop_duplicates()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().str.replace(r"\s+", " ", regex=True)

    return df
```

This is the basic skeleton. You add the rules for your own dataset on top. For example, my version of the function also has the city dictionary and the date format.

## One last note

Cleaning is never really "done". While building a model or drawing a chart, a new oddity can turn up and force you to go back and fix things. That's normal. What matters is that you keep every change you make in code, meaning you never patch anything by hand in Excel. Three months from now, when someone asks "where did this number come from?", your answer will be ready.
