import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image
import json
import uuid
import shutil

VERSION = [0, 0, 1]
IMAGE_OPTIONS = ["오리지널", "16x16", "32x32"]

def edit_pack_info():
    resource_pack_info_window = tk.Toplevel(root)
    resource_pack_info_window.title("리소스팩의 정보를 알려주세요!")
    tk.Label(resource_pack_info_window, text="리소스팩 이름").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(resource_pack_info_window, text="리소스팩 설명").grid(row=2, column=0, padx=5, pady=5)
    tk.Label(resource_pack_info_window, text="버전").grid(row=3, column=0, padx=5, pady=5)
    name_var = tk.StringVar()
    name_entry = tk.Entry(resource_pack_info_window, textvariable=name_var, width=30)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    description_var = tk.StringVar()
    description_entry = tk.Entry(resource_pack_info_window, textvariable=description_var, width=30)
    description_entry.grid(row=2, column=1, padx=5, pady=5)
    version_var = tk.StringVar(value="0.0.1")
    version_entry = tk.Entry(resource_pack_info_window, textvariable=version_var, width=30)
    version_entry.grid(row=3, column=1, padx=5, pady=5)
    def _():
        resource_pack_info_window.destroy()
        edit_item_info(name_var.get(), description_var.get(), version_var.get())
    tk.Button(resource_pack_info_window, text="😻 | 다음으로 이동하기", command=_, width=20).grid(row=4, columnspan=2, pady=10)

def edit_item_info(pack_name, pack_description, pack_version):
    input_window = tk.Toplevel(root)
    input_window.title("아이템의 정보를 알려주세요!")
    header_frame = tk.Frame(input_window, padx=10, pady=10)
    header_frame.pack(fill="x", pady=5)
    tk.Label(header_frame, text="원본 파일 이름", width=20).grid(row=0, column=0, padx=5, pady=5)
    tk.Label(header_frame, text="크기", width=20).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(header_frame, text="식별자", width=20).grid(row=0, column=2, padx=5, pady=5)
    png_files = [f for f in os.listdir("before") if f.endswith(".png")]
    if not png_files:
        messagebox.showinfo("알림", "이미지 파일이 존재하지 않습니다")
        input_window.destroy()
        return
    info = []
    for file in png_files:
        frame = tk.Frame(input_window, padx=10, pady=5)
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=file, width=20).grid(row=0, column=0, padx=5, pady=5)
        size_var = tk.StringVar(value=IMAGE_OPTIONS[0])
        size_menu = ttk.Combobox(frame, textvariable=size_var, values=IMAGE_OPTIONS, state="readonly", width=18)
        size_menu.grid(row=0, column=1, padx=5, pady=5)
        identifier_var = tk.StringVar(value=file)
        identifier_entry = tk.Entry(frame, textvariable=identifier_var, width=20)
        identifier_entry.grid(row=0, column=2, padx=5, pady=5)
        info.append((file, size_var, identifier_var))

    def process_files():
        pack_folder = os.path.join("after", pack_name)
        if not os.path.exists(pack_folder):
            os.makedirs(pack_folder)
        manifest_data = {
            "format_version": 2,
            "header": {
                "description": pack_description,
                "name": pack_name,
                "uuid": str(uuid.uuid4()),
                "version": list(map(int, pack_version.split("."))),
                "min_engine_version": [1, 20, 60]
            },
            "modules": [
                {
                    "type": "resources",
                    "uuid": str(uuid.uuid4()),
                    "version": list(map(int, pack_version.split(".")))
                }
            ]
        }
        manifest_path = os.path.join(pack_folder, "manifest.json")
        with open(manifest_path, 'w') as manifest_file:
            json.dump(manifest_data, manifest_file, ensure_ascii=False, indent=2)
        items_folder = os.path.join(pack_folder, "textures", "items")
        os.makedirs(items_folder)
        item_texture_data = {
            "resource_pack_name": "vanilla",
            "texture_name": "atlas.items",
            "texture_data": {}
        }
        item_texture_path = os.path.join(pack_folder, "textures", "item_texture.json")
        for file, size_var, identifier_var in info:
            file_path = os.path.join("before", file)
            img = Image.open(file_path)
            size = size_var.get()
            if size != IMAGE_OPTIONS[0]:
                width, height = map(int, size.split("x"))
                img = img.resize((width, height), Image.LANCZOS)
            identifier = identifier_var.get()
            img.save(os.path.join(items_folder, file))
            item_texture_data["texture_data"][identifier] = {
                "textures": f"textures/items/{file.replace(".png", "")}"
            }
        with open(item_texture_path, 'w') as item_texture_file:
            json.dump(item_texture_data, item_texture_file, ensure_ascii=False, indent=2)
        shutil.make_archive(pack_folder, "zip", pack_folder)
        shutil.rmtree(pack_folder)
        messagebox.showinfo("📥", f"리소스팩을 성공적으로 제작하였습니다! {pack_folder.replace("after/", "")}.zip을 확인해주세요")
        input_window.destroy()
    tk.Button(input_window, text="🐶 | 리소스팩 생성하기", command=process_files, width=20).pack(pady=10)



if not os.path.exists("before"):
    os.makedirs("before")
if not os.path.exists("after"):
    os.makedirs("after")

root = tk.Tk()
root.title("반가워요!")

file_frame = tk.Frame(root, padx=10, pady=10)
file_frame.pack(fill="x")

tk.Button(root, text="😆 | 리소스팩 생성하기 ", command=edit_pack_info, width=20).pack(pady=5)
tk.Button(root, text="😎 | 제작자 @sleepysoong", command=root.quit, width=20).pack(pady=5)

for widget in file_frame.winfo_children():
    widget.destroy()

tk.Label(file_frame, text="아주 쉽게 아이템 리소스팩을 제작해보세요!\n\n* 로드 된 이미지 목록").pack(pady=2)

png_files = [f for f in os.listdir("before") if f.endswith(".png")]
for file in png_files:
    tk.Label(file_frame, text=file).pack(pady=2)

root.mainloop()