import sys
import os
import shutil
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QFormLayout, QMessageBox

class MinecraftPackCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Minecraft Pack Creator')
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.texture_path = QLineEdit(self)
        self.model_path = QLineEdit(self)
        self.item_name = QLineEdit(self)
        self.custom_model_data = QLineEdit(self)
        
        form_layout.addRow('Texture File:', self.create_file_picker(self.texture_path))
        form_layout.addRow('Model File:', self.create_file_picker(self.model_path))
        form_layout.addRow('Item Name:', self.item_name)
        form_layout.addRow('Custom Model Data:', self.custom_model_data)
        
        layout.addLayout(form_layout)
        
        generate_button = QPushButton('Generate Resource Pack', self)
        generate_button.clicked.connect(self.generate_pack)
        layout.addWidget(generate_button)
        
        self.setLayout(layout)

    def create_file_picker(self, line_edit):
        container = QWidget()
        layout = QVBoxLayout(container)
        line_edit.setReadOnly(True)
        layout.addWidget(line_edit)
        button = QPushButton('Browse', self)
        button.clicked.connect(lambda: self.browse_file(line_edit))
        layout.addWidget(button)
        return container

    def browse_file(self, line_edit):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'All Files (*)', options=options)
        if file_path:
            line_edit.setText(file_path)

    def generate_pack(self):
        texture_path = self.texture_path.text()
        model_path = self.model_path.text()
        item_name = self.item_name.text()
        custom_model_data = self.custom_model_data.text()
        
        if not texture_path or not model_path or not item_name or not custom_model_data:
            QMessageBox.warning(self, 'Input Error', 'All fields must be filled out.')
            return
        
        try:
            custom_model_data = int(custom_model_data)
        except ValueError:
            QMessageBox.warning(self, 'Input Error', 'Custom Model Data must be a number.')
            return
        
        pack_path = 'resources/generated_pack'
        if os.path.exists(pack_path):
            shutil.rmtree(pack_path)
        
        os.makedirs(f'{pack_path}/assets/minecraft/textures/item', exist_ok=True)
        os.makedirs(f'{pack_path}/assets/minecraft/models/item', exist_ok=True)
        
        texture_filename = os.path.basename(texture_path)
        model_filename = os.path.basename(model_path)
        
        new_texture_path = f'{pack_path}/assets/minecraft/textures/item/{texture_filename}'
        new_model_path = f'{pack_path}/assets/minecraft/models/item/{model_filename}'
        
        shutil.copy(texture_path, new_texture_path)
        shutil.copy(model_path, new_model_path)
        
        with open(new_model_path, 'r') as model_file:
            model_json = json.load(model_file)
        
        model_json['textures'] = {
            "layer0": f"item/{texture_filename.split('.')[0]}"
        }
        
        with open(new_model_path, 'w') as model_file:
            json.dump(model_json, model_file, indent=4)
        
        overrides_json = {
            "parent": "item/generated",
            "textures": {
                "layer0": "item/diamond_sword"  # default texture if needed
            },
            "overrides": [
                {
                    "predicate": {
                        "custom_model_data": custom_model_data
                    },
                    "model": f"item/{model_filename.split('.')[0]}"
                }
            ]
        }
        
        with open(f'{pack_path}/assets/minecraft/models/item/{item_name}.json', 'w') as f:
            json.dump(overrides_json, f, indent=4)
        
        pack_meta = {
            "pack": {
                "pack_format": 6,
                "description": "Custom Texture Pack"
            }
        }
        
        with open(f'{pack_path}/pack.mcmeta', 'w') as f:
            json.dump(pack_meta, f, indent=4)
        
        shutil.make_archive('resource_pack', 'zip', pack_path)
        QMessageBox.information(self, 'Success', 'Resource pack generated successfully!')

def main():
    app = QApplication(sys.argv)
    window = MinecraftPackCreator()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
