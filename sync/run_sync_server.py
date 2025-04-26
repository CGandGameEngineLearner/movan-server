#!/usr/bin/env python3
import subprocess
import time
import os
import argparse
from typing import List, Dict, Any, Optional

class ProcessManager:
    def __init__(self):
        self.processes: Dict[int, subprocess.Popen] = {}
        
    def start_process(self, script_path: str, args: List[Any]) -> int:
        """启动一个Python脚本进程，传入指定参数"""
        cmd = ["python", script_path] + [str(arg) for arg in args]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        process_id = process.pid
        self.processes[process_id] = process
        print(f"启动进程 PID={process_id}: {' '.join(cmd)}")
        return process_id
    
    def start_multiple(self, script_path: str, param_sets: List[List[Any]]) -> List[int]:
        """使用多组参数启动多个进程"""
        return [self.start_process(script_path, params) for params in param_sets]
    
    def monitor_all(self, timeout: Optional[float] = None) -> Dict[int, int]:
        """监控所有进程，返回进程ID和退出码的映射"""
        start_time = time.time()
        result = {}
        
        while self.processes and (timeout is None or time.time() - start_time < timeout):
            for pid in list(self.processes.keys()):
                process = self.processes[pid]
                return_code = process.poll()
                
                if return_code is not None:
                    stdout, stderr = process.communicate()
                    print(f"进程 {pid} 已结束，退出码: {return_code}")
                    if stdout:
                        print(f"标准输出:\n{stdout[:200]}..." if len(stdout) > 200 else f"标准输出:\n{stdout}")
                    if stderr:
                        print(f"错误输出:\n{stderr[:200]}..." if len(stderr) > 200 else f"错误输出:\n{stderr}")
                        
                    result[pid] = return_code
                    del self.processes[pid]
            
            if self.processes:
                time.sleep(0.1)
                
        return result
    
    def terminate_all(self) -> None:
        """终止所有正在运行的进程"""
        for pid, process in list(self.processes.items()):
            print(f"终止进程 {pid}")
            process.terminate()
        
        # 给进程一点时间优雅地退出
        time.sleep(0.5)
        
        # 强制结束仍在运行的进程
        for pid, process in list(self.processes.items()):
            if process.poll() is None:
                print(f"强制结束进程 {pid}")
                process.kill()
                
        self.processes.clear()

def main():
    parser = argparse.ArgumentParser(description="启动多个Python脚本进程，并传入不同的参数")
    parser.add_argument("script", help="要运行的Python脚本路径")
    parser.add_argument("--params", nargs="+", action="append", 
                       help="每个进程的参数集，可多次指定，如 --params 1 2 3 --params 4 5 6")
    parser.add_argument("--timeout", type=float, default=None, 
                       help="监控超时时间（秒），不指定则一直监控到所有进程结束")
    
    args = parser.parse_args()
    
    # 检查脚本是否存在
    if not os.path.isfile(args.script):
        print(f"错误: 找不到脚本文件 '{args.script}'")
        return 1
    
    # 如果没有提供参数集，提供一个空参数的默认值
    param_sets = args.params if args.params else [[]]
    
    manager = ProcessManager()
    try:
        manager.start_multiple(args.script, param_sets)
        manager.monitor_all(args.timeout)
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在停止所有进程...")
    finally:
        manager.terminate_all()
    
    return 0

if __name__ == "__main__":
    exit(main())