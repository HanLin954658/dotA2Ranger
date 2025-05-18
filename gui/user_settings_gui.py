import tkinter as tk
from tkinter import ttk
from config.config_loader import load_config, save_config

def get_user_settings():
    """显示GUI并返回用户设置"""
    config = load_config()

    # 默认值
    default_var1 = config.get("Var1", "收起")
    default_nandu = config.get("nandu", 6)
    default_use_money = config.get("useMoney", 0)

    # 创建主窗口
    root = tk.Tk()
    root.title("变量选择器")
    root.geometry("400x300")
    root.resizable(False, False)

    # 创建框架
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)

    # 变量存储
    var1_var = tk.StringVar(value=default_var1)
    nandu_var = tk.IntVar(value=default_nandu)
    use_money_var = tk.BooleanVar(value=bool(default_use_money))

    # Var1 选择
    ttk.Label(frame, text="Var1:").grid(row=0, column=0, sticky=tk.W, pady=10)
    var1_values = ["开局", "重开", "难度", "收起"]
    var1_combo = ttk.Combobox(frame, textvariable=var1_var, values=var1_values, width=15)
    var1_combo.grid(row=0, column=1, sticky=tk.W, pady=10)

    # nandu 选择
    ttk.Label(frame, text="难度 (0-9):").grid(row=1, column=0, sticky=tk.W, pady=10)
    nandu_scale = ttk.Scale(frame, variable=nandu_var, from_=1, to=25, orient=tk.HORIZONTAL, length=200)
    nandu_scale.grid(row=1, column=1, sticky=tk.W, pady=10)
    nandu_value_label = ttk.Label(frame, text=str(default_nandu))
    nandu_value_label.grid(row=1, column=2, padx=10)

    def update_nandu_label(event):
        nandu_value_label.config(text=str(nandu_var.get()))

    nandu_scale.bind("<Motion>", update_nandu_label)
    nandu_scale.bind("<ButtonRelease-1>", update_nandu_label)

    # useMoney 选择
    ttk.Label(frame, text="使用金钱:").grid(row=2, column=0, sticky=tk.W, pady=10)
    use_money_check = ttk.Checkbutton(frame, variable=use_money_var)
    use_money_check.grid(row=2, column=1, sticky=tk.W, pady=10)

    # 结果
    result_var = tk.StringVar()
    result_label = ttk.Label(frame, textvariable=result_var, justify=tk.LEFT)
    result_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

    # 返回值
    result = None

    # 确认按钮回调
    def on_confirm():
        nonlocal result
        # 获取当前值
        var1 = var1_var.get()
        nandu = nandu_var.get()
        use_money = use_money_var.get()

        # 保存配置
        config = {
            "Var1": var1,
            "nandu": nandu,
            "useMoney": use_money
        }
        save_config(config)

        # 显示结果
        result_var.set(f"已保存配置:\nVar1: {var1}\n难度: {nandu}\n使用金钱: {'是' if use_money else '否'}")

        # 存储结果并关闭窗口
        result = (var1, nandu - 1, use_money)
        root.after(1000, root.destroy)

    # 确认按钮
    confirm_btn = ttk.Button(frame, text="确认", command=on_confirm)
    confirm_btn.grid(row=4, column=0, columnspan=2, pady=20)

    # 窗口关闭时保存配置
    def on_closing():
        save_config({
            "Var1": var1_var.get(),
            "nandu": nandu_var.get(),
            "useMoney": 1 if use_money_var.get() else 0
        })
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 运行主循环
    root.mainloop()

    # 返回结果
    return result