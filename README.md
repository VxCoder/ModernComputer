# modern_computer

## 项目说明
基于python和系统库实现,未参考java源码。只基于书内思路和规范实现。通过所有提供的测试文件。

## 文件说明
* BaseUtils.py  
通用工具包. 
* Assembler.py  
汇编器 asm -> hack
* Vmtranslator.py  
虚拟机  vm -> asm
* JackAnalyzer_xml.py  
编译器 只生成xml结果 过渡版本
* JackAnalyzer.py  
编译器完全版 jack -> vm


## 遗留问题
最后Pong项目 通过工具生成.asm和.hack后, CPU Emulator 装载后提示"Program too large".
优化OS库导入机制(只加载程序依赖的OS函数)，还是未能解决。