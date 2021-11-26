import sys

from utils.io import cover_batch, cover_phynum, cover_ne, run_batch

if __name__ == "__main__":
    # 读取阶段。
    if len(sys.argv) != 2:
        print("[Error] Stage required")
        exit(-1)
    stage = sys.argv[1]

    # 写入阶段配置。
    cover_batch(stage)
    cover_phynum(stage)
    cover_ne(stage)

    # 运行批处理文件。
    run_batch()
