// Variables globales
let currentSection = 'dashboard';
let charts = {};
let categorias = [];
let transacciones = [];

// Configuración de colores para gráficas
const chartColors = {
    primary: '#FF6B35',
    secondary: '#FF8C42',
    accent: '#FFD23F',
    success: '#2ECC71',
    danger: '#E74C3C',
    info: '#3498DB',
    warning: '#F39C12',
    dark: '#2C3E50'
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        await loadCategorias();
        await loadDashboard();
        setupEventListeners();
        setTodayDate();
    } catch (error) {
        console.error('Error inicializando la aplicación:', error);
        showAlert('Error al cargar la aplicación', 'danger');
    }
}

// Gestión de secciones
function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Mostrar la sección seleccionada
    document.getElementById(sectionName + '-section').classList.add('active');
    
    // Actualizar navegación
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
    
    currentSection = sectionName;
    
    // Cargar datos específicos de la sección
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'transacciones':
            loadTransacciones();
            break;
        case 'estadisticas':
            loadEstadisticas();
            break;
        case 'categorias':
            loadCategoriasSection();
            break;
    }
}

// API Calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`/api${endpoint}`, config);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const data = await apiCall('/dashboard');
        
        // Actualizar tarjetas de resumen
        document.getElementById('balance-total').textContent = formatCurrency(data.balance_total);
        document.getElementById('ingresos-mes').textContent = formatCurrency(data.ingresos_mes);
        document.getElementById('gastos-mes').textContent = formatCurrency(data.gastos_mes);
        document.getElementById('balance-mes').textContent = formatCurrency(data.balance_mes);
        
        // Mostrar transacciones recientes
        displayRecentTransactions(data.ultimas_transacciones);
        
        // Cargar gráfica mensual
        await loadMonthlyChart();
        
    } catch (error) {
        console.error('Error cargando dashboard:', error);
        showAlert('Error al cargar el dashboard', 'danger');
    }
}

async function loadMonthlyChart() {
    try {
        const data = await apiCall('/estadisticas/resumen-mensual');
        
        const ctx = document.getElementById('monthlyChart').getContext('2d');
        
        if (charts.monthly) {
            charts.monthly.destroy();
        }
        
        charts.monthly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.mes),
                datasets: [
                    {
                        label: 'Ingresos',
                        data: data.map(item => item.ingresos),
                        backgroundColor: chartColors.success,
                        borderColor: chartColors.success,
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false,
                    },
                    {
                        label: 'Gastos',
                        data: data.map(item => item.gastos),
                        backgroundColor: chartColors.danger,
                        borderColor: chartColors.danger,
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                weight: 'bold'
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    } catch (error) {
        console.error('Error cargando gráfica mensual:', error);
    }
}

function displayRecentTransactions(transactions) {
    const container = document.getElementById('recent-transactions');
    
    if (!transactions || transactions.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay transacciones recientes</p>';
        return;
    }
    
    container.innerHTML = transactions.map(transaction => `
        <div class="transaction-item ${transaction.tipo}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="transaction-description">${transaction.descripcion}</div>
                    <div class="transaction-category">
                        <i class="fas fa-tag me-1"></i>${transaction.categoria_nombre}
                    </div>
                    <small class="text-muted">${formatDate(transaction.fecha)}</small>
                </div>
                <div class="transaction-amount ${transaction.tipo}">
                    ${transaction.tipo === 'ingreso' ? '+' : '-'}${formatCurrency(Math.abs(transaction.monto))}
                </div>
            </div>
        </div>
    `).join('');
}

// Transacciones
async function loadTransacciones() {
    try {
        const data = await apiCall('/transacciones');
        transacciones = data;
        displayTransactions(data);
        populateFilterCategories();
    } catch (error) {
        console.error('Error cargando transacciones:', error);
        showAlert('Error al cargar las transacciones', 'danger');
    }
}

function displayTransactions(transactions) {
    const tbody = document.getElementById('transactions-table');
    
    if (!transactions || transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay transacciones</td></tr>';
        return;
    }
    
    tbody.innerHTML = transactions.map(transaction => `
        <tr>
            <td>${formatDate(transaction.fecha)}</td>
            <td>${transaction.descripcion}</td>
            <td>
                <span class="d-inline-flex align-items-center">
                    <span class="category-color me-2" style="background-color: ${transaction.categoria_color}"></span>
                    ${transaction.categoria_nombre}
                </span>
            </td>
            <td>
                <span class="badge badge-${transaction.tipo}">
                    ${transaction.tipo === 'ingreso' ? 'Ingreso' : 'Gasto'}
                </span>
            </td>
            <td class="transaction-amount ${transaction.tipo}">
                ${transaction.tipo === 'ingreso' ? '+' : '-'}${formatCurrency(Math.abs(transaction.monto))}
            </td>
            <td>
                <button class="btn btn-outline-secondary btn-sm me-1" onclick="editTransaction(${transaction.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteTransaction(${transaction.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Categorías
async function loadCategorias() {
    try {
        const data = await apiCall('/categorias');
        categorias = data;
        return data;
    } catch (error) {
        console.error('Error cargando categorías:', error);
        throw error;
    }
}

async function loadCategoriasSection() {
    try {
        await loadCategorias();
        
        const gastos = categorias.filter(cat => cat.tipo === 'gasto');
        const ingresos = categorias.filter(cat => cat.tipo === 'ingreso');
        
        displayCategories('expense-categories', gastos);
        displayCategories('income-categories', ingresos);
    } catch (error) {
        console.error('Error cargando sección de categorías:', error);
        showAlert('Error al cargar las categorías', 'danger');
    }
}

function displayCategories(containerId, categories) {
    const container = document.getElementById(containerId);
    
    if (!categories || categories.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay categorías</p>';
        return;
    }
    
    container.innerHTML = categories.map(category => `
        <div class="category-item">
            <span class="category-color" style="background-color: ${category.color}"></span>
            <span class="category-name">${category.nombre}</span>
            <div class="ms-auto">
                <button class="btn btn-outline-secondary btn-sm me-1" onclick="editCategory(${category.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteCategory(${category.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Estadísticas
async function loadEstadisticas() {
    try {
        await Promise.all([
            loadCategoryChart(),
            loadTrendsChart()
        ]);
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
        showAlert('Error al cargar las estadísticas', 'danger');
    }
}

async function loadCategoryChart() {
    try {
        const data = await apiCall('/estadisticas/por-categoria?tipo=gasto');
        
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        if (charts.category) {
            charts.category.destroy();
        }
        
        charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.categoria),
                datasets: [{
                    data: data.map(item => item.total),
                    backgroundColor: data.map(item => item.color),
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const item = data[context.dataIndex];
                                return `${item.categoria}: ${formatCurrency(item.total)} (${item.porcentaje}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error cargando gráfica de categorías:', error);
    }
}

async function loadTrendsChart() {
    try {
        const data = await apiCall('/estadisticas/tendencias');
        
        const ctx = document.getElementById('trendsChart').getContext('2d');
        
        if (charts.trends) {
            charts.trends.destroy();
        }
        
        charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.periodo),
                datasets: [
                    {
                        label: 'Ingresos',
                        data: data.map(item => item.ingresos),
                        borderColor: chartColors.success,
                        backgroundColor: chartColors.success + '20',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Gastos',
                        data: data.map(item => item.gastos),
                        borderColor: chartColors.danger,
                        backgroundColor: chartColors.danger + '20',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                weight: 'bold'
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    } catch (error) {
        console.error('Error cargando gráfica de tendencias:', error);
    }
}

// Modales y formularios
function showAddTransactionModal(tipo) {
    document.getElementById('transaction-type').value = tipo;
    document.getElementById('transactionModalTitle').textContent = 
        tipo === 'ingreso' ? 'Agregar Ingreso' : 'Agregar Gasto';
    
    populateTransactionCategories(tipo);
    
    const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
    modal.show();
}

function populateTransactionCategories(tipo) {
    const select = document.getElementById('transaction-category');
    const filteredCategories = categorias.filter(cat => cat.tipo === tipo);
    
    select.innerHTML = filteredCategories.map(cat => 
        `<option value="${cat.id}">${cat.nombre}</option>`
    ).join('');
}

function populateFilterCategories() {
    const select = document.getElementById('filter-categoria');
    select.innerHTML = '<option value="">Todas las categorías</option>' +
        categorias.map(cat => 
            `<option value="${cat.id}">${cat.nombre} (${cat.tipo})</option>`
        ).join('');
}

async function saveTransaction() {
    try {
        const formData = {
            descripcion: document.getElementById('transaction-description').value,
            monto: parseFloat(document.getElementById('transaction-amount').value),
            categoria_id: parseInt(document.getElementById('transaction-category').value),
            fecha: document.getElementById('transaction-date').value,
            tipo: document.getElementById('transaction-type').value
        };
        
        await apiCall('/transacciones', 'POST', formData);
        
        // Cerrar modal y limpiar formulario
        bootstrap.Modal.getInstance(document.getElementById('transactionModal')).hide();
        document.getElementById('transactionForm').reset();
        
        // Recargar datos
        await loadDashboard();
        if (currentSection === 'transacciones') {
            await loadTransacciones();
        }
        
        showAlert('Transacción guardada correctamente', 'success');
    } catch (error) {
        console.error('Error guardando transacción:', error);
        showAlert('Error al guardar la transacción', 'danger');
    }
}

function showAddCategoryModal() {
    const modal = new bootstrap.Modal(document.getElementById('categoryModal'));
    modal.show();
}

async function saveCategory() {
    try {
        const formData = {
            nombre: document.getElementById('category-name').value,
            tipo: document.getElementById('category-type').value,
            color: document.getElementById('category-color').value
        };
        
        await apiCall('/categorias', 'POST', formData);
        
        // Cerrar modal y limpiar formulario
        bootstrap.Modal.getInstance(document.getElementById('categoryModal')).hide();
        document.getElementById('categoryForm').reset();
        
        // Recargar datos
        await loadCategorias();
        await loadCategoriasSection();
        
        showAlert('Categoría guardada correctamente', 'success');
    } catch (error) {
        console.error('Error guardando categoría:', error);
        showAlert('Error al guardar la categoría', 'danger');
    }
}

// Funciones de utilidad
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function setTodayDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('transaction-date').value = today;
}

function showAlert(message, type) {
    // Crear elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Event listeners
function setupEventListeners() {
    // Filtros de transacciones
    ['filter-tipo', 'filter-categoria', 'filter-fecha-inicio', 'filter-fecha-fin'].forEach(id => {
        document.getElementById(id).addEventListener('change', filterTransactions);
    });
}

function filterTransactions() {
    const tipo = document.getElementById('filter-tipo').value;
    const categoriaId = document.getElementById('filter-categoria').value;
    const fechaInicio = document.getElementById('filter-fecha-inicio').value;
    const fechaFin = document.getElementById('filter-fecha-fin').value;
    
    let filtered = [...transacciones];
    
    if (tipo) {
        filtered = filtered.filter(t => t.tipo === tipo);
    }
    
    if (categoriaId) {
        filtered = filtered.filter(t => t.categoria_id == categoriaId);
    }
    
    if (fechaInicio) {
        filtered = filtered.filter(t => t.fecha >= fechaInicio);
    }
    
    if (fechaFin) {
        filtered = filtered.filter(t => t.fecha <= fechaFin);
    }
    
    displayTransactions(filtered);
}

// Funciones de edición y eliminación (placeholder)
async function deleteTransaction(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta transacción?')) {
        try {
            await apiCall(`/transacciones/${id}`, 'DELETE');
            await loadDashboard();
            if (currentSection === 'transacciones') {
                await loadTransacciones();
            }
            showAlert('Transacción eliminada correctamente', 'success');
        } catch (error) {
            console.error('Error eliminando transacción:', error);
            showAlert('Error al eliminar la transacción', 'danger');
        }
    }
}

async function deleteCategory(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta categoría?')) {
        try {
            await apiCall(`/categorias/${id}`, 'DELETE');
            await loadCategorias();
            await loadCategoriasSection();
            showAlert('Categoría eliminada correctamente', 'success');
        } catch (error) {
            console.error('Error eliminando categoría:', error);
            showAlert('Error al eliminar la categoría', 'danger');
        }
    }
}

function editTransaction(id) {
    showAlert('Función de edición en desarrollo', 'info');
}

function editCategory(id) {
    showAlert('Función de edición en desarrollo', 'info');
}

