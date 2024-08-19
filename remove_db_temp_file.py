import os

def delete_files_with_prefix(directory, prefix):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 如果文件名以指定的前缀开头
        if filename.startswith(prefix):
            # 构造文件的完整路径
            file_path = os.path.join(directory, filename)
            try:
                # 删除文件
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

# 示例用法
directory = "/home/kuaipan/memdb/"  # 替换为你的目录路径
prefix = "file::"  # 替换为你的前缀字符串
delete_files_with_prefix(directory, prefix)