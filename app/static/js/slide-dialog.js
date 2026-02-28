class SlideDialog {
    constructor(options = {}) {
        this.options = {
            title: '确认操作',
            content: '',
            confirmText: '确认',
            cancelText: '取消',
            confirmClass: 'btn-danger',
            cancelClass: 'btn-secondary',
            onConfirm: null,
            onCancel: null,
            ...options
        };
        
        this.overlay = null;
        this.dialog = null;
        this.create();
    }
    
    create() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'slide-dialog-overlay';
        
        this.dialog = document.createElement('div');
        this.dialog.className = 'slide-dialog';
        
        this.dialog.innerHTML = `
            <div class="slide-dialog-header">
                <h5 class="mb-0">${this.options.title}</h5>
                <button type="button" class="btn-close" aria-label="Close"></button>
            </div>
            <div class="slide-dialog-body">
                ${this.options.content}
            </div>
            <div class="slide-dialog-footer">
                <button type="button" class="btn ${this.options.cancelClass} cancel-btn">
                    ${this.options.cancelText}
                </button>
                <button type="button" class="btn ${this.options.confirmClass} confirm-btn">
                    ${this.options.confirmText}
                </button>
            </div>
        `;
        
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.dialog);
        
        this.bindEvents();
    }
    
    bindEvents() {
        const closeBtn = this.dialog.querySelector('.btn-close');
        const cancelBtn = this.dialog.querySelector('.cancel-btn');
        const confirmBtn = this.dialog.querySelector('.confirm-btn');
        
        closeBtn.addEventListener('click', () => this.close());
        cancelBtn.addEventListener('click', () => this.close());
        confirmBtn.addEventListener('click', () => this.confirm());
        this.overlay.addEventListener('click', () => this.close());
    }
    
    show() {
        setTimeout(() => {
            this.overlay.classList.add('show');
            this.dialog.classList.add('show');
        }, 10);
    }
    
    close() {
        this.overlay.classList.remove('show');
        this.dialog.classList.remove('show');
        
        if (this.options.onCancel) {
            this.options.onCancel();
        }
        
        setTimeout(() => {
            this.destroy();
        }, 300);
    }
    
    confirm() {
        this.overlay.classList.remove('show');
        this.dialog.classList.remove('show');
        
        if (this.options.onConfirm) {
            this.options.onConfirm();
        }
        
        setTimeout(() => {
            this.destroy();
        }, 300);
    }
    
    destroy() {
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
        }
        if (this.dialog && this.dialog.parentNode) {
            this.dialog.parentNode.removeChild(this.dialog);
        }
    }
}

function showSlideDialog(options) {
    const dialog = new SlideDialog(options);
    dialog.show();
    return dialog;
}

function confirmAction(title, message, onConfirm) {
    return showSlideDialog({
        title: title,
        content: `<p class="mb-0">${message}</p>`,
        confirmText: '确认',
        cancelText: '取消',
        confirmClass: 'btn-danger',
        onConfirm: onConfirm
    });
}

function deleteConfirm(entityName, onConfirm) {
    return confirmAction(
        '确认删除',
        `确定要删除这个${entityName}吗？此操作不可撤销。`,
        onConfirm
    );
}
