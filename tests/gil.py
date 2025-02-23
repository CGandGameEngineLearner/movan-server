import sys
import sysconfig
 
print(sysconfig.get_config_var("Py_GIL_DISABLED")) #输出为“1”时表示GIL已经被禁用
print(sys._is_gil_enabled()) #输出为False表示GIL在运行时未被启用