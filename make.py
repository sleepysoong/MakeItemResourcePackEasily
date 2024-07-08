import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image as PILImage
import json
import uuid
import shutil

VERSION = [1, 1, 0]
IMAGE_OPTIONS = ["오리지널", "16x16", "32x32"]


class Image:
    def __init__(self, file_path):
        self.file_path = file_path
        self.img = PILImage.open(file_path)

    def resize(self, width, height):
        self.img = self.img.resize((width, height), PILImage.LANCZOS)

    def save(self, directory):
        self.img.save(os.path.join(directory, os.path.basename(self.file_path)))


class ResourcePack:
    def __init__(self, name, description, version):
        self.name = name
        self.description = description
        self.version = version
        self.images = []

    def add_image(self, image, identifier):
        self.images.append((image, identifier))

    def process(self, directory, option):
        folder = os.path.join(directory, self.name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        manifest_data = {
            "format_version": 2,
            "header": {
                "description": self.description,
                "name": self.name,
                "uuid": str(uuid.uuid4()),
                "version": list(map(int, self.version.split("."))),
                "min_engine_version": [1, 20, 60]
            },
            "modules": [
                {
                    "type": "resources",
                    "uuid": str(uuid.uuid4()),
                    "version": list(map(int, self.version.split(".")))
                }
            ]
        }
        manifest_path = os.path.join(folder, "manifest.json")
        with open(manifest_path, 'w') as manifest_file:
            json.dump(manifest_data, manifest_file, ensure_ascii=False, indent=2)
        items_folder = os.path.join(folder, "textures", "items")
        os.makedirs(items_folder)
        item_texture_data = {
            "resource_pack_name": "vanilla",
            "texture_name": "atlas.items",
            "texture_data": {}
        }
        item_texture_path = os.path.join(folder, "textures", "item_texture.json")
        for image, identifier in self.images:
            image.save(items_folder)
            item_texture_data["texture_data"][identifier] = {
                "textures": f"textures/items/{os.path.basename(image.file_path).replace('.png', '')}"
            }
        with open(item_texture_path, 'w') as item_texture_file:
            json.dump(item_texture_data, item_texture_file, ensure_ascii=False, indent=2)

        if option == "zip":
            shutil.make_archive(folder, "zip", folder)
            shutil.rmtree(folder)
        elif option == "mcpack":
            shutil.make_archive(folder, "zip", folder)
            os.rename(f"{folder}.zip", f"{folder}.mcpack")
            shutil.rmtree(folder)


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
        edit_item_info(ResourcePack(name_var.get(), description_var.get(), version_var.get()))

    tk.Button(resource_pack_info_window, text="😻 | 다음으로 이동하기", command=_, width=20).grid(row=4, columnspan=2, pady=10)


def edit_item_info(resource_pack):
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
    for file in png_files:
        frame = tk.Frame(input_window, padx=10, pady=5)
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=file, width=20).grid(row=0, column=0, padx=5, pady=5)
        size_var = tk.StringVar(value=IMAGE_OPTIONS[0])
        size_menu = ttk.Combobox(frame, textvariable=size_var, values=IMAGE_OPTIONS, state="readonly", width=18)
        size_menu.grid(row=0, column=1, padx=5, pady=5)
        identifier_var = tk.StringVar(value=os.path.splitext(file)[0])
        identifier_entry = tk.Entry(frame, textvariable=identifier_var, width=20)
        identifier_entry.grid(row=0, column=2, padx=5, pady=5)
        image = Image(os.path.join("before", file))
        resource_pack.add_image(image, identifier_var.get())

    def process_files():
        save_window = tk.Toplevel(input_window)
        save_window.title("저장 방식 선택")

        def save_pack(option):
            resource_pack.process("after", option)
            save_window.destroy()
            input_window.destroy()
            messagebox.showinfo("📥", f"리소스팩을 성공적으로 제작하였습니다! after 폴더를 확인해주세요!")

        tk.Button(save_window, text="🤐 | zip 파일로 저장하기", command=lambda: save_pack("zip"), width=20).pack(pady=5)
        tk.Button(save_window, text="⚒️ | mcpack 파일로 저장하기", command=lambda: save_pack("mcpack"), width=20).pack(pady=5)
        tk.Button(save_window, text="📁 | 폴더로 저장하기", command=lambda: save_pack("folder"), width=20).pack(pady=5)

    tk.Button(input_window, text="🐶 | 리소스팩 생성하기", command=process_files, width=20).pack(pady=10)


def refresh_image_list():
    for widget in file_frame.winfo_children():
        widget.destroy()
    tk.Label(file_frame, text="아주 쉽게 아이템 리소스팩을 제작해보세요!\n\n* 로드 된 이미지 목록").pack(pady=2)
    png_files = [f for f in os.listdir("before") if f.endswith(".png")]
    for file in png_files:
        tk.Label(file_frame, text=file).pack(pady=2)


if not os.path.exists("before"):
    os.makedirs("before")
if not os.path.exists("after"):
    os.makedirs("after")

root = tk.Tk()
root.title("반가워요!")

file_frame = tk.Frame(root, padx=10, pady=10)
file_frame.pack(fill="x")

tk.Button(root, text="😆 | 리소스팩 생성하기 ", command=edit_pack_info, width=20).pack(pady=5)
tk.Button(root, text="🔄 | 이미지 목록 새로고침", command=refresh_image_list, width=20).pack(pady=5)
tk.Button(root, text="😎 | 제작자 @sleepysoong", command=root.quit, width=20).pack(pady=5)

refresh_image_list()
root.mainloop()
