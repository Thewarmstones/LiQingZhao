# 可视化雷达图
#


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os
import json

input_folder = './clean_data'  # 输出文件夹路径
output_folder = './vis_img'  # 输出文件夹路径
os.makedirs(output_folder, exist_ok=True)



# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 数据准备
labels = ['对话能力', '角色一致性', '角色扮演吸引力', '人格回测','角色幻觉']  # 指标名称
data = {
    'ChatGLM3-6B': [0.8, 0.7, 0.6, 0.9,0.9],
    'Qwen-14B': [0.9,0.7, 0.8, 0.9, 0.6],
    'Xingchen': [0.9, 0.6, 0.8, 0.7,0.9],
    'GPT-3.5': [0.6, 0.9, 0.7, 0.8,0.5],
    'GPT-4': [0.9, 0.8,0.5, 0.6, 0.7],
    'Minimax': [0.8,0.9, 0.7, 0.9, 0.6],
    'BC-NPC-Turbo': [0.7,0.8, 0.9, 0.8, 0.9]
}

# 将数据闭合（首尾相连）
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # 闭合角度

# 创建绘图
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), dpi=300)

# 自定义颜色列表
colors = [
    '#FFA07A',  # 肉桂色
    '#ADD8E6',  # 浅蓝色
    '#FFD700',  # 金色
    '#FFC0CB',  # 玫瑰红
    '#FF69B4',  # 粉红色
    '#BA55D3',  # 紫罗兰色
    '#87CEEB'   # 浅蓝色
]

# 绘制每组数据
for i, (label, values) in enumerate(data.items()):
    values += values[:1]  # 闭合数据
    ax.plot(angles, values, color=colors[i], linewidth=2, label=label)
    ax.fill(angles, values, color=colors[i], alpha=0.25)

# 设置同心圆参考线
ax.set_rlim(0, 1)  # 设置径向范围
ax.set_rticks([0.2, 0.4, 0.6, 0.8])  # 设置径向刻度
ax.grid(True)

# 设置轴标签
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=12)

# 添加图例
ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=10)

# 设置标题
ax.set_title('模型性能对比', fontsize=14)


# 保存高清图片
plt.savefig(os.path.join(output_folder,'radar_chart.png'), dpi=600, bbox_inches='tight')  # 保存为PNG格式
plt.show()