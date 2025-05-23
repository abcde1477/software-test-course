import subprocess
import os


log_output_dir = "output"
os.makedirs(log_output_dir, exist_ok=True)


scripts = {
    "boundary value analysis": os.path.join("black_box", "boundary value analysis.py"),
    "equivalence partitioning": os.path.join("black_box", "equivalence partitioning.py"),
    "fuzzing test": os.path.join("black_box", "fuzzing test.py"),
    "property_base_test": os.path.join("black_box", "property_base_test.py"),
    
    "all-def": os.path.join("white_box", "all-def.py"),
    "all-use": os.path.join("white_box", "all-use.py"),
}

for name, path in scripts.items():
    abs_path = os.path.abspath(path)
    output_path = os.path.join(log_output_dir, f"{name}.out.txt")

    print(f"正在执行 {name} ({abs_path})...")

    with open(output_path, "w") as outfile:
        result = subprocess.run(
            ["python", abs_path],
            stdout=outfile,
            stderr=subprocess.STDOUT
        )

    if result.returncode != 0:
        print(f"{name} 执行失败，返回码：{result.returncode}，输出写入：{output_path}")
    else:
        print(f"{name} 执行完成，输出写入：{output_path}\n")