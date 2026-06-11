import os
import sys
from blind_watermark import WaterMark

# ========== 配置区 ==========
DEFAULT_PWD_IMG = 1
DEFAULT_PWD_WM = 1
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ===========================
#密码只能为数字 例如 1，123，999等。不要出现字符
def safe_write_info(filename, content):
    filepath = os.path.join(SCRIPT_DIR, filename)
    try:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except PermissionError:
                print(f"⚠️ 请关闭正在打开的文件 {filename} 后重试")
                return False
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except PermissionError:
        print(f"❌ 权限不足，无法写入 {filename}")
        return False

def safe_read_info(filename):
    filepath = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip().splitlines()
    except:
        return None

def check_path(path, name="图片"):
    """检查路径是否包含中文"""
    if any('\u4e00' <= char <= '\u9fff' for char in path):
        print(f"⚠️ 警告：{name}路径包含中文字符，可能导致嵌入失败。")
        print("   建议将图片移到纯英文路径（如 D:\\images\\）后重试。")
        return False
    return True

def get_passwords():
    print(f"\n当前默认密码: img={DEFAULT_PWD_IMG}, wm={DEFAULT_PWD_WM}")
    ch = input("使用默认密码？(回车=是, n=自定义): ").strip().lower()
    if ch == 'n':
        try:
            p1 = int(input("请输入 password_img: "))
            p2 = int(input("请输入 password_wm: "))
            return p1, p2
        except:
            print("输入无效，使用默认密码")
            return DEFAULT_PWD_IMG, DEFAULT_PWD_WM
    return DEFAULT_PWD_IMG, DEFAULT_PWD_WM

def embed_text():
    print("\n--- 嵌入文本水印 ---")
    img_path = input("拖入原始图片: ").strip().strip('"')
    if not os.path.exists(img_path):
        print("❌ 文件不存在")
        return
    wm_str = input("输入水印文字 (回车使用默认): ").strip()
    if wm_str == "":
        wm_str = "@guofei9987 开源万岁！"
    out_path = input("输出路径 (回车自动生成): ").strip().strip('"')
    if out_path == "":
        base, _ = os.path.splitext(img_path)
        out_path = f"{base}_text_wm.png"
    pwd_img, pwd_wm = get_passwords()

    try:
        bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
        bwm.read_img(img_path)
        bwm.read_wm(wm_str, mode='str')
        bwm.embed(out_path)
        wm_len = len(bwm.wm_bit)
        safe_write_info("last_text_wm.txt", f"{wm_len}\n{pwd_img}\n{pwd_wm}")
        print(f"✅ 嵌入成功！\n   输出: {out_path}\n   水印长度: {wm_len}")
    except Exception as e:
        print(f"❌ 嵌入失败: {e}")

def extract_text():
    print("\n--- 提取文本水印 ---")
    img_path = input("拖入含水印的图片: ").strip().strip('"')
    if not os.path.exists(img_path):
        print("❌ 文件不存在")
        return
    lines = safe_read_info("last_text_wm.txt")
    if lines and len(lines) >= 3:
        wm_len = int(lines[0])
        pwd_img = int(lines[1])
        pwd_wm = int(lines[2])
        print(f"📌 使用上次保存信息: 长度={wm_len}, 密码=({pwd_img},{pwd_wm})")
        if input("使用这些信息？(回车=是, n=手动): ").lower() == 'n':
            try:
                wm_len = int(input("请输入水印长度: "))
                pwd_img = int(input("password_img: ") or DEFAULT_PWD_IMG)
                pwd_wm = int(input("password_wm: ") or DEFAULT_PWD_WM)
            except:
                print("❌ 输入无效")
                return
    else:
        try:
            wm_len = int(input("请输入水印长度: "))
            pwd_img = int(input("password_img: ") or DEFAULT_PWD_IMG)
            pwd_wm = int(input("password_wm: ") or DEFAULT_PWD_WM)
        except:
            print("❌ 输入无效")
            return
    try:
        bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
        res = bwm.extract(img_path, wm_shape=wm_len, mode='str')
        print(f"✅ 提取结果: {res}" if res else "❌ 提取失败")
    except Exception as e:
        print(f"❌ 提取出错: {e}")

def embed_image():
    """图片水印嵌入 - 与单独脚本完全一致"""
    print("\n--- 嵌入图片水印 ---")
    img_path = input("拖入原始图片: ").strip().strip('"')
    if not os.path.exists(img_path):
        print("❌ 原始图片不存在")
        return
    wm_path = input("拖入作为水印的图片: ").strip().strip('"')
    if not os.path.exists(wm_path):
        print("❌ 水印图片不存在")
        return
    out_path = input("输出路径 (回车自动生成): ").strip().strip('"')
    if out_path == "":
        base, _ = os.path.splitext(img_path)
        out_path = f"{base}_img_wm.png"
    pwd_img, pwd_wm = get_passwords()

    check_path(img_path, "原始图片")
    check_path(wm_path, "水印图片")

    try:
        bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
        bwm.read_img(img_path)
        bwm.read_wm(wm_path, mode='img')
        bwm.embed(out_path)

        import cv2
        temp_wm = cv2.imread(wm_path)
        if temp_wm is not None:
            h, w = temp_wm.shape[:2]
        else:
            h, w = 0, 0
            print("⚠️ 无法读取水印尺寸，请手动记录")
        safe_write_info("last_img_wm.txt", f"{h}\n{w}\n{pwd_img}\n{pwd_wm}")
        print(f"✅ 嵌入成功！\n   输出: {out_path}\n   水印尺寸: {h}x{w}")
    except Exception as e:
        print(f"❌ 嵌入失败: {e}")
        print("提示：请确保图片路径不含中文，且图片文件未损坏。")

def extract_image():
    """图片水印提取 - 与单独脚本完全一致"""
    print("\n--- 提取图片水印 ---")
    img_path = input("拖入含水印的图片: ").strip().strip('"')
    if not os.path.exists(img_path):
        print("❌ 文件不存在")
        return

    lines = safe_read_info("last_img_wm.txt")
    if lines and len(lines) >= 4:
        h = int(lines[0])
        w = int(lines[1])
        pwd_img = int(lines[2])
        pwd_wm = int(lines[3])
        print(f"📌 上次保存: 尺寸={h}x{w}, 密码=({pwd_img},{pwd_wm})")
        if input("使用这些信息？(回车=是, n=手动): ").lower() == 'n':
            try:
                h = int(input("水印高度: "))
                w = int(input("水印宽度: "))
                pwd_img = int(input("password_img: ") or DEFAULT_PWD_IMG)
                pwd_wm = int(input("password_wm: ") or DEFAULT_PWD_WM)
            except:
                print("❌ 输入无效")
                return
    else:
        try:
            h = int(input("水印高度: "))
            w = int(input("水印宽度: "))
            pwd_img = int(input("password_img: ") or DEFAULT_PWD_IMG)
            pwd_wm = int(input("password_wm: ") or DEFAULT_PWD_WM)
        except:
            print("❌ 输入无效")
            return

    out_path = input("提取出的水印保存路径 (回车自动生成): ").strip().strip('"')
    if out_path == "":
        base, _ = os.path.splitext(img_path)
        out_path = f"{base}_extracted_wm.png"

    try:
        bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
        bwm.extract(filename=img_path, wm_shape=(h, w), out_wm_name=out_path, mode='img')
        print(f"✅ 水印图片已保存至: {out_path}")
    except Exception as e:
        print(f"❌ 提取失败: {e}")

def main():
    while True:
        print("\n" + "="*40)
        print("     盲水印工具 - 完美整合版")
        print("="*40)
        print("1. 嵌入文本水印")
        print("2. 提取文本水印")
        print("3. 嵌入图片水印")
        print("4. 提取图片水印")
        print("5. 退出")
        choice = input("请选择 (1-5): ").strip()
        if choice == '1':
            embed_text()
        elif choice == '2':
            extract_text()
        elif choice == '3':
            embed_image()
        elif choice == '4':
            extract_image()
        elif choice == '5':
            print("再见！")
            break
        else:
            print("无效输入")
        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"发生未捕获的错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
