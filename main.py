# main.py
from optimizer import run_optimizer
import os
import config

def main():
    """
    程式主入口。
    負責執行策略優化器。
    """
    print("--- 策略優化器啟動 ---")
    
    # 確保輸出目錄存在
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    run_optimizer()
    
    print("\n--- 所有優化流程已完成 ---")

if __name__ == '__main__':
    main()