const API_URL = 'http://127.0.0.1:8000';
let listaProjetosCache = [];

// ==========================================
// RENDERIZAÇÃO PRINCIPAL (Sem Piscar na tela)
// ==========================================
async function carregarDashboard(silencioso = false) {
    const grid = document.getElementById('projetos-grid');
    
    // Só exibe mensagem de loading se for a primeira vez carregando
    if (!silencioso && grid.innerHTML === '') {
        grid.innerHTML = '<p style="color: var(--text-muted);">Sincronizando workspace...</p>';
    }

    try {
        const resProjetos = await fetch(`${API_URL}/projetos/`);
        listaProjetosCache = await resProjetos.json();

        // Variável temporária para montar o HTML sem mexer na tela real ainda
        let novoConteudoHTML = '';

        if (listaProjetosCache.length === 0) {
            novoConteudoHTML = '<p style="color: var(--text-muted);">Nenhum projeto no workspace. Crie o primeiro!</p>';
        } else {
            // Busca tarefas para todos os projetos
            for (const projeto of listaProjetosCache) {
                const resTarefas = await fetch(`${API_URL}/tarefas/projeto/${projeto.id}`);
                const tarefas = await resTarefas.json();

                let tarefasHTML = '';
                if (tarefas.length === 0) {
                    tarefasHTML = '<li class="tarefa-item" style="color: var(--text-muted); justify-content: center; font-style: italic;">Nenhuma tarefa vinculada.</li>';
                } else {
                    tarefas.forEach(t => {
                        const classeBadge = obterClasseBadge(t.status);
                        // Escapando aspas para evitar quebra no HTML
                        const tituloLimpo = t.titulo.replace(/'/g, "\\'").replace(/"/g, "&quot;");
                        
                        tarefasHTML += `
                            <li class="tarefa-item">
                                <span>${t.titulo}</span>
                                <div class="tarefa-acoes">
                                    <span class="badge ${classeBadge}" title="Mudar status" onclick="alternarStatus(${t.id}, '${tituloLimpo}', '${t.status}')">${t.status}</span>
                                    <button class="btn-icon danger" title="Excluir tarefa" onclick="deletarTarefa(${t.id})"><i class="fa-solid fa-trash-can"></i></button>
                                </div>
                            </li>
                        `;
                    });
                }

                // Protegendo os dados do projeto para a função de edição
                const nomeLimpo = projeto.nome.replace(/'/g, "\\'");
                const descLimpa = (projeto.descricao || '').replace(/'/g, "\\'");

                novoConteudoHTML += `
                    <div class="projeto-card">
                        <div class="projeto-header">
                            <div class="projeto-info">
                                <h3>${projeto.nome}</h3>
                                <p>${projeto.descricao || 'Sem descrição'}</p>
                            </div>
                            <div class="projeto-acoes">
                                <button class="btn-icon" title="Editar Projeto" onclick="abrirModalProjeto(${projeto.id}, '${nomeLimpo}', '${descLimpa}')"><i class="fa-solid fa-pen"></i></button>
                                <button class="btn-icon danger" title="Excluir Projeto" onclick="deletarProjeto(${projeto.id})"><i class="fa-solid fa-trash-can"></i></button>
                            </div>
                        </div>
                        <ul class="tarefas-lista">
                            ${tarefasHTML}
                        </ul>
                    </div>
                `;
            }
        }

        // Troca a tela inteira de uma só vez (Evita o piscar)
        grid.innerHTML = novoConteudoHTML;

    } catch (erro) {
        console.error("Erro:", erro);
        grid.innerHTML = '<p style="color: #ef4444;">Falha ao conectar com o servidor. O FastAPI está rodando?</p>';
    }
}

// ==========================================
// CRUD DE PROJETOS
// ==========================================
async function salvarProjeto(event) {
    event.preventDefault();
    const id = document.getElementById('projeto-id').value;
    const nome = document.getElementById('input-nome-projeto').value;
    const descricao = document.getElementById('input-desc-projeto').value;

    const metodo = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/projetos/${id}` : `${API_URL}/projetos/`;

    try {
        const res = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, descricao })
        });

        if (res.ok) {
            fecharModal('modal-projeto');
            carregarDashboard(true); // Passa 'true' para atualizar silenciosamente
        } else {
            alert('Erro ao salvar o projeto.');
        }
    } catch (erro) { console.error(erro); }
}

async function deletarProjeto(id) {
    if (!confirm('ATENÇÃO: Excluir este projeto apagará todas as tarefas vinculadas. Continuar?')) return;
    
    try {
        const res = await fetch(`${API_URL}/projetos/${id}`, { method: 'DELETE' });
        if (res.ok) carregarDashboard(true);
    } catch (erro) { console.error(erro); }
}

// ==========================================
// CRUD DE TAREFAS
// ==========================================
async function salvarTarefa(event) {
    event.preventDefault();
    const titulo = document.getElementById('input-titulo-tarefa').value;
    const projeto_id = parseInt(document.getElementById('select-projeto').value);

    try {
        const res = await fetch(`${API_URL}/tarefas/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, projeto_id })
        });

        if (res.ok) {
            fecharModal('modal-tarefa');
            carregarDashboard(true);
        }
    } catch (erro) { console.error(erro); }
}

async function alternarStatus(id, titulo, statusAtual) {
    const proximos = { 'Pendente': 'Em Andamento', 'Em Andamento': 'Concluída', 'Concluída': 'Pendente' };
    const novoStatus = proximos[statusAtual] || 'Pendente';

    try {
        const res = await fetch(`${API_URL}/tarefas/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, status: novoStatus })
        });
        if (res.ok) carregarDashboard(true);
    } catch (erro) { console.error(erro); }
}

async function deletarTarefa(id) {
    if (!confirm('Excluir esta tarefa?')) return;
    try {
        const res = await fetch(`${API_URL}/tarefas/${id}`, { method: 'DELETE' });
        if (res.ok) carregarDashboard(true);
    } catch (erro) { console.error(erro); }
}

// ==========================================
// CONTROLE DE MODAIS
// ==========================================
function abrirModalProjeto(id = '', nome = '', descricao = '') {
    document.getElementById('projeto-id').value = id;
    document.getElementById('input-nome-projeto').value = nome;
    document.getElementById('input-desc-projeto').value = descricao;
    
    document.getElementById('titulo-modal-projeto').innerText = id ? 'Editar Projeto' : 'Novo Projeto';
    document.getElementById('modal-projeto').classList.remove('hidden');
}

function abrirModalTarefa() {
    if (listaProjetosCache.length === 0) {
        alert("Você precisa criar um projeto primeiro!");
        return;
    }

    const select = document.getElementById('select-projeto');
    select.innerHTML = '';
    listaProjetosCache.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.nome;
        select.appendChild(opt);
    });

    document.getElementById('modal-tarefa').classList.remove('hidden');
}

function fecharModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
    if(modalId === 'modal-projeto') document.getElementById('form-projeto').reset();
    if(modalId === 'modal-tarefa') document.getElementById('form-tarefa').reset();
}

function obterClasseBadge(status) {
    const mapas = { 'Pendente': 'pendente', 'Em Andamento': 'em-andamento', 'Concluída': 'concluida' };
    return mapas[status] || 'pendente';
}

// Start
carregarDashboard();