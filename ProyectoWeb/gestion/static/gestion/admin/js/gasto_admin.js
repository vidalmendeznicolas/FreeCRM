// JavaScript para mejorar la interfaz de subida de archivos en el admin de gastos
document.addEventListener('DOMContentLoaded', function() {
    const facturaField = document.getElementById('id_factura');
    
    if (facturaField) {
        // Crear contenedor personalizado
        const fileContainer = document.createElement('div');
        fileContainer.className = 'file-upload-container';
        fileContainer.innerHTML = `
            <div class="upload-icon">
                📁
            </div>
            <p><strong>Subir Factura</strong></p>
            <p class="allowed-formats">Formatos permitidos: PDF, JPG, PNG (máx. 5MB)</p>
            <p style="color: #6c757d; font-size: 0.9em;">Arrastra el archivo aquí o haz clic para seleccionar</p>
        `;
        
        // Insertar después del campo
        facturaField.parentNode.insertBefore(fileContainer, facturaField.nextSibling);
        
        // Ocultar el campo original
        facturaField.style.display = 'none';
        
        // Mostrar archivo actual si existe
        if (facturaField.value) {
            showCurrentFile(facturaField.value);
        }
        
        // Eventos de drag & drop
        fileContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
            fileContainer.classList.add('dragover');
        });
        
        fileContainer.addEventListener('dragleave', function(e) {
            e.preventDefault();
            fileContainer.classList.remove('dragover');
        });
        
        fileContainer.addEventListener('drop', function(e) {
            e.preventDefault();
            fileContainer.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
        
        // Click para seleccionar archivo
        fileContainer.addEventListener('click', function() {
            facturaField.click();
        });
        
        // Cambio en el campo original
        facturaField.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFile(this.files[0]);
            }
        });
    }
    
    function handleFile(file) {
        // Validar tipo de archivo
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
            alert('Solo se permiten archivos PDF, JPG o PNG.');
            return;
        }
        
        // Validar tamaño (5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('El archivo es demasiado grande. Máximo 5MB.');
            return;
        }
        
        // Crear FileList simulado
        const dt = new DataTransfer();
        dt.items.add(file);
        facturaField.files = dt.files;
        
        // Mostrar información del archivo
        showFileInfo(file);
    }
    
    function showFileInfo(file) {
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info';
        fileInfo.innerHTML = `
            <div class="filename">${file.name}</div>
            <div class="filesize">${formatFileSize(file.size)}</div>
        `;
        
        // Remover info anterior si existe
        const existingInfo = fileContainer.querySelector('.file-info');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        fileContainer.appendChild(fileInfo);
    }
    
    function showCurrentFile(filename) {
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info';
        fileInfo.innerHTML = `
            <div class="filename">${filename}</div>
            <div class="filesize">Archivo actual</div>
        `;
        fileContainer.appendChild(fileInfo);
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}); 