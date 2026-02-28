class FileBrowser {
  constructor() {
    this.leftPath = '/mnt';
    this.rightPath = '/media/tape';
    this.leftSelectedItems = new Set();
    this.rightSelectedItems = new Set();
    this.pollingInterval = null;
    
    this.init();
  }

  init() {
    this.bindEvents();
    this.loadDirectory('left', this.leftPath);
    this.loadDirectory('right', this.rightPath);
    this.loadTransfers();
    this.startPolling();
  }

  bindEvents() {
    // 左右全选
    document.getElementById('leftSelectAll').addEventListener('change', (e) => {
      this.handleSelectAll('left', e.target.checked);
    });
    
    document.getElementById('rightSelectAll').addEventListener('change', (e) => {
      this.handleSelectAll('right', e.target.checked);
    });
  }

  async loadDirectory(side, path) {
    try {
      const response = await fetch(`/api/browser/list?path=${encodeURIComponent(path)}`);
      const data = await response.json();
      
      if (data.success) {
        if (side === 'left') {
          this.leftPath = data.path;
          this.renderFileList('left', data.items);
          this.renderBreadcrumb('left', data.path);
        } else {
          this.rightPath = data.path;
          this.renderFileList('right', data.items);
          this.renderBreadcrumb('right', data.path);
        }
      } else {
        alert('加载目录失败: ' + data.message);
      }
    } catch (error) {
      console.error('加载目录失败:', error);
    }
  }

  renderBreadcrumb(side, path) {
    const breadcrumbId = side === 'left' ? 'leftBreadcrumb' : 'rightBreadcrumb';
    const breadcrumb = document.getElementById(breadcrumbId);
    breadcrumb.innerHTML = '';
    
    const parts = path.split('/').filter(p => p);
    let currentPath = '';
    
    // 根目录
    const liRoot = document.createElement('li');
    liRoot.className = 'breadcrumb-item';
    liRoot.innerHTML = `<a href="#" data-path="${side === 'left' ? '/mnt' : '/media/tape'}">${side === 'left' ? '/mnt' : '/media/tape'}</a>`;
    liRoot.querySelector('a').addEventListener('click', (e) => {
      e.preventDefault();
      this.loadDirectory(side, e.target.dataset.path);
    });
    breadcrumb.appendChild(liRoot);
    
    // 子目录
    for (let i = 0; i < parts.length; i++) {
      currentPath += '/' + parts[i];
      const fullPath = (side === 'left' ? '/mnt' : '/media/tape') + currentPath;
      
      const li = document.createElement('li');
      if (i === parts.length - 1) {
        li.className = 'breadcrumb-item active';
        li.textContent = parts[i];
      } else {
        li.className = 'breadcrumb-item';
        li.innerHTML = `<a href="#" data-path="${fullPath}">${parts[i]}</a>`;
        li.querySelector('a').addEventListener('click', (e) => {
          e.preventDefault();
          this.loadDirectory(side, e.target.dataset.path);
        });
      }
      breadcrumb.appendChild(li);
    }
  }

  renderFileList(side, items) {
    const tbodyId = side === 'left' ? 'leftFileTableBody' : 'rightFileTableBody';
    const tbody = document.getElementById(tbodyId);
    tbody.innerHTML = '';
    
    items.forEach(item => {
      const tr = document.createElement('tr');
      
      // 复选框
      const tdCheck = document.createElement('td');
      if (!item.is_parent) {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'item-checkbox';
        checkbox.dataset.path = item.path;
        checkbox.dataset.side = side;
        
        const selectedSet = side === 'left' ? this.leftSelectedItems : this.rightSelectedItems;
        checkbox.checked = selectedSet.has(item.path);
        
        checkbox.addEventListener('change', (e) => {
          this.handleItemSelect(side, item.path, e.target.checked);
        });
        
        tdCheck.appendChild(checkbox);
      }
      tr.appendChild(tdCheck);
      
      // 名称
      const tdName = document.createElement('td');
      const icon = item.type === 'directory' ? '📂' : '📄';
      tdName.innerHTML = `<a href="#" class="item-link" data-path="${item.path}" data-type="${item.type}" data-side="${side}">${icon} ${item.name}</a>`;
      
      const link = tdName.querySelector('.item-link');
      link.addEventListener('click', (e) => {
        e.preventDefault();
        if (item.type === 'directory') {
          this.loadDirectory(side, item.path);
        }
      });
      
      tr.appendChild(tdName);
      
      // 大小
      const tdSize = document.createElement('td');
      tdSize.textContent = item.is_parent ? '' : this.formatBytes(item.size);
      tr.appendChild(tdSize);
      
      tbody.appendChild(tr);
    });
    
    this.updateSelectionUI(side);
  }

  handleSelectAll(side, checked) {
    const checkboxes = document.querySelectorAll(`#${side === 'left' ? 'left' : 'right'}FileTableBody .item-checkbox`);
    const selectedSet = side === 'left' ? this.leftSelectedItems : this.rightSelectedItems;
    
    checkboxes.forEach(cb => {
      cb.checked = checked;
      const path = cb.dataset.path;
      if (checked) {
        selectedSet.add(path);
      } else {
        selectedSet.delete(path);
      }
    });
    
    this.updateSelectionUI(side);
  }

  handleItemSelect(side, path, checked) {
    const selectedSet = side === 'left' ? this.leftSelectedItems : this.rightSelectedItems;
    
    if (checked) {
      selectedSet.add(path);
    } else {
      selectedSet.delete(path);
    }
    
    this.updateSelectionUI(side);
  }

  updateSelectionUI(side) {
    const selectedSet = side === 'left' ? this.leftSelectedItems : this.rightSelectedItems;
    const selectAll = side === 'left' ? document.getElementById('leftSelectAll') : document.getElementById('rightSelectAll');
    const transferRightBtn = document.getElementById('transferRightBtn');
    const transferLeftBtn = document.getElementById('transferLeftBtn');
    
    // 更新全选状态
    const visibleCheckboxes = document.querySelectorAll(`#${side === 'left' ? 'left' : 'right'}FileTableBody .item-checkbox`);
    selectAll.checked = visibleCheckboxes.length > 0 && 
                         selectedSet.size === visibleCheckboxes.length;
    
    // 更新传输按钮状态
    transferRightBtn.disabled = this.leftSelectedItems.size === 0;
    transferLeftBtn.disabled = this.rightSelectedItems.size === 0;
  }

  refreshBrowser(side) {
    if (side === 'left') {
      this.loadDirectory('left', this.leftPath);
    } else {
      this.loadDirectory('right', this.rightPath);
    }
  }

  async transferToRight() {
    if (this.leftSelectedItems.size === 0) {
      alert('请先选择要传输的文件');
      return;
    }
    
    const sourcePaths = Array.from(this.leftSelectedItems);
    const targetPath = this.rightPath;
    const transferType = document.getElementById('transferType').value;
    
    try {
      const response = await fetch('/api/transfer/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          source_paths: sourcePaths,
          target_path: targetPath,
          transfer_type: transferType,
          transfer_direction: 'container_to_tape'
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert('传输任务已启动！');
        this.leftSelectedItems.clear();
        this.refreshBrowser('left');
        this.loadTransfers();
      } else {
        alert('启动失败: ' + data.message);
      }
    } catch (error) {
      console.error('传输启动失败:', error);
      alert('传输启动失败');
    }
  }

  async transferToLeft() {
    if (this.rightSelectedItems.size === 0) {
      alert('请先选择要传输的文件');
      return;
    }
    
    const sourcePaths = Array.from(this.rightSelectedItems);
    const targetPath = this.leftPath;
    const transferType = document.getElementById('transferType').value;
    
    try {
      const response = await fetch('/api/transfer/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          source_paths: sourcePaths,
          target_path: targetPath,
          transfer_type: transferType,
          transfer_direction: 'tape_to_container'
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert('传输任务已启动！');
        this.rightSelectedItems.clear();
        this.refreshBrowser('right');
        this.loadTransfers();
      } else {
        alert('启动失败: ' + data.message);
      }
    } catch (error) {
      console.error('传输启动失败:', error);
      alert('传输启动失败');
    }
  }

  async loadTransfers() {
    try {
      const response = await fetch('/api/transfer/list');
      const data = await response.json();
      
      if (data.success) {
        this.renderTransfers(data.transfers);
      }
    } catch (error) {
      console.error('加载传输列表失败:', error);
    }
  }

  renderTransfers(transfers) {
    const container = document.getElementById('transfersContainer');
    
    if (transfers.length === 0) {
      container.innerHTML = '<p class="text-muted">暂无传输任务</p>';
      return;
    }
    
    container.innerHTML = transfers.map(t => `
      <div class="progress-item mb-3 p-3 border rounded">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div>
            <strong>${t.transfer_type === 'copy' ? '复制' : '移动'}</strong>
            <span class="ms-2">${t.transfer_direction === 'container_to_tape' ? '💻 → 📼' : '📼 → 💻'}</span>
            <span class="ms-2">${t.file_count} 个文件</span>
          </div>
          <span class="status-text status-${t.status}">${this.getStatusText(t.status)}</span>
        </div>
        ${t.status === 'in_progress' ? `
          <div class="mb-2">
            <small class="text-muted">当前文件: ${t.current_file || '准备中...'}</small>
          </div>
        ` : ''}
        <div class="progress mb-2" style="height: 8px;">
          <div class="progress-bar" role="progressbar" 
               style="width: ${t.progress}%" 
               aria-valuenow="${t.progress}" 
               aria-valuemin="0" 
               aria-valuemax="100">
          </div>
        </div>
        <div class="d-flex justify-content-between small text-muted">
          <span>${this.formatBytes(t.transferred_size)} / ${this.formatBytes(t.total_size)}</span>
          <span>${t.progress.toFixed(1)}%</span>
        </div>
        ${t.average_speed ? `
          <div class="mt-2 small text-muted">
            平均速度: ${t.average_speed.toFixed(1)} MB/s
          </div>
        ` : ''}
        ${t.error_message ? `
          <div class="mt-2 text-danger small">${t.error_message}</div>
        ` : ''}
      </div>
    `).join('');
  }

  getStatusText(status) {
    const statusMap = {
      'pending': '等待中',
      'in_progress': '传输中',
      'completed': '已完成',
      'failed': '失败',
      'cancelled': '已取消'
    };
    return statusMap[status] || status;
  }

  formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  startPolling() {
    // 每 2 秒刷新一次传输状态
    this.pollingInterval = setInterval(() => {
      this.loadTransfers();
    }, 2000);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  }
}

// 全局函数
function refreshBrowser(side) {
  window.fileBrowser.refreshBrowser(side);
}

function transferToRight() {
  window.fileBrowser.transferToRight();
}

function transferToLeft() {
  window.fileBrowser.transferToLeft();
}

function loadTransfers() {
  window.fileBrowser.loadTransfers();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
  window.fileBrowser = new FileBrowser();
});
