const API_URL = 'http://127.0.0.1:8000';
let listaProjetosCache = [];

// Carrega os projetos e tarefas no Dashboard
async function carregarDashboard() {
    const grid = document.getElementById('projetos-grid');
    grid.innerHTML = '<p style="color: var(--text-muted);">Carregando dados...</p>';

    try {
        const resProjetos = await fetch(`${API_URL}/projetos/`);
        listaProjetosCache = await resProjetos.json();

        grid.innerHTML = '';

        if (listaProjetosCache.length === 0) {
            grid.innerHTML = '<p style="color: var(--text-muted);">Nenhum projeto cadastrado.</p>';
            return;
        }

        for (const projeto of listaProjetosCache) {
            const resTarefas = await fetch(`${API_URL}/tarefas/projeto/${projeto.id}`);
            const tarefas = await resTarefas.json();

            const card = document.createElement('div');
            card.className = 'projeto-card';

            let tarefasHTML = '';
            if (tarefas.length === 0) {
                tarefasHTML = '<li class="tarefa-item" style="color: var(--text-muted);"><em>Nenhuma tarefa vinculada.</em></li>';
            } else {
                tarefas.forEach(tarefa => {
                    const classeBadge = obterClasseBadge(tarefa.status);
                    
                    // Escapa aspas para evitar erros de sintaxe no HTML inline
                    const tituloEscapado = tarefa.titulo.replace(/'/g, "\\'");

                    tarefasHTML += `
                        <li class="tarefa-item">
                            <span>${tarefa.titulo}</span>
                            <div class="tarefa-acoes">
                                <span class="badge ${classeBadge}" 
                                      title="Clique para mudar o status"
                                      onclick="alternarStatus(${tarefa.id}, '${tituloEscapado}', '${tarefa.status}')">
                                    ${tarefa.status}
                                </span>
                                <button class="btn-deletar" 
                                        title="Excluir tarefa" 
                                        onclick="deletarTarefa(${tarefa.id})">✕</button>
                            </div>
                        </li>
                    `;
                });
            }

            card.innerHTML = `
                <h3>${projeto.nome}</h3>
                <p>${projeto.descricao || 'Sem descrição.'}</p>
                <ul class="tarefas-lista">
                    ${tarefasHTML}
                </ul>
            `;

            grid.appendChild(card);
        }
    } catch (erro) {
        console.error("Erro ao carregar dashboard:", erro);
        grid.innerHTML = '<p style="color: #ef4444;">Erro de conexão com o servidor.</p>';
    }
}

// PUT: Alterna o status da tarefa no banco
async function alternarStatus(id, titulo, statusAtual) {
    const proximosStatus = {
        'Pendente': 'Em Andamento',
        'Em Andamento': 'Concluída',
        'Concluída': 'Pendente'
    };

    const novoStatus = proximosStatus[statusAtual] || 'Pendente';

    try {
        const resposta = await fetch(`${API_URL}/tarefas/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                titulo: titulo,
                status: novoStatus
            })
        });

        if (resposta.ok) {
            carregarDashboard();
        } else {
            alert('Erro ao atualizar status.');
        }
    } catch (erro) {
        console.error('Erro na requisição PUT:', erro);
    }
}

// DELETE: Exclui a tarefa do banco
async function deletarTarefa(id) {
    if (!confirm('Deseja realmente excluir esta tarefa?')) return;

    try {
        const resposta = await fetch(`${API_URL}/tarefas/${id}`, {
            method: 'DELETE'
        });

        if (resposta.ok) {
            carregarDashboard();
        } else {
            alert('Erro ao excluir tarefa.');
        }
    } catch (erro) {
        console.error('Erro na requisição DELETE:', erro);
    }
}

// POST: Cria uma nova tarefa
async function salvarTarefa(event) {
    event.preventDefault();

    const titulo = document.getElementById('input-titulo').value;
    const projeto_id = parseInt(document.getElementById('select-projeto').value);

    try {
        const resposta = await fetch(`${API_URL}/tarefas/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, projeto_id })
        });

        if (resposta.ok) {
            fecharModal();
            carregarDashboard();
        } else {
            alert('Erro ao salvar tarefa.');
        }
    } catch (erro) {
        console.error('Erro na requisição POST:', erro);
    }
}

// Controle do Modal
function abrirModal() {
    const select = document.getElementById('select-projeto');
    select.innerHTML = '';

    listaProjetosCache.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.textContent = p.nome;
        select.appendChild(option);
    });

    document.getElementById('modal-container').classList.remove('hidden');
}

function fecharModal() {
    document.getElementById('modal-container').classList.add('hidden');
    document.getElementById('form-tarefa').reset();
}

function obterClasseBadge(status) {
    switch (status) {
        case 'Pendente': return 'pendente';
        case 'Em Andamento': return 'em-andamento';
        case 'Concluída': return 'concluida';
        default: return 'pendente';
    }
}

// Inicialização
carregarDashboard();