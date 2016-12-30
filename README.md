# MTK自动patch脚本
## 描述
自动合入MTK patch，仅适用于SVN环境。修改过的Android源码不要使用这个脚本，因为该脚本采用的是覆盖的方式进行patch，所以如果非纯净的代码会丢失掉一些修改。 
## 环境
1. linux
2. python 2.7  

## 使用
1. 下载脚本 `git clone https://github.com/she11/mtk_auto_patch.git`
2. 将脚本文件和patch文件放入同一目录
3. 赋予脚本执行权限 `chmod +x patch.py`
4. `./patch.py` 执行  


附上文件目录结构

```
├─┬ ALPS-MP-XXXX-AUSXXXX
│ ├─ abi
│ ├─ ...
│ ├─ frameworks
│ ├─ ...
│ └─ Makefile
├─ patch.py
├─ ALPS_P1.tar.gz
├─ ALPS_p2.tar.gz
└─ ...
```


# enjoy it！
