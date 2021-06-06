# 筛选姓名首字母

从标准输入中读入字符串,计算拼音首字母,与目标比较，输出满足条件的字符串和行号

## 用法

`-t <target-initials>` : 指定目标首字母拼写

## 示例

假设我们有`list.txt`文件，它的内容为

```
<学号>       <姓名>    <学院>
...
20XXXXXXX9   陈XX      XXX
...
```

那么我们可以用下面的命令快速地筛选出这一行内容中的姓名和行号

```bash
cat list.txt  | awk '{print $2}' | python3 name-filter.py -t cxx

# output:
# 2XX : 陈XX
```

可以根据输出的行号得到原来文件中目标行的所有信息

```bash
tail list.txt -n 2XX | head -n 1
```
