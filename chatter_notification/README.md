# Project Chatter Follower Notifications

Módulo personalizado para Odoo 19.

## Notificações do Chatter

Mantém o comportamento existente do módulo:

- seguidores internos de tarefas recebem as mensagens manuais no Inbox do Odoo;
- não é necessário estar atribuído à tarefa;
- o autor não recebe a própria notificação;
- mensagens técnicas/automáticas não são tratadas como mensagens manuais.

## Nome apresentado nas notificações

Para threads associadas a `project.task`, o nome enviado ao Mail/Discuss é:

`Cliente | Projeto | Tarefa`

Exemplo:

`Cliente ABC | Pesquisa & Desenvolvimento | Usability review`

Se não existir cliente:

`Pesquisa & Desenvolvimento | Usability review`

Se não existir projeto/cliente:

`Usability review`

O cliente é obtido primeiro de `task.partner_id`; se estiver vazio, é usado
`task.project_id.partner_id`.

O nome real da tarefa na base de dados não é alterado.

## Versão 19.0.1.3.1

Corrige uma recursão infinita da versão 19.0.1.3.0.

A versão anterior chamava `store.add(..., as_thread=True)` dentro de
`_thread_to_store()`. Como `Store.add(..., as_thread=True)` volta a chamar
`_thread_to_store()`, isso provocava `RecursionError`.

Esta versão deixa o Odoo serializar normalmente a thread e, no fim, atualiza
diretamente o registo `mail.thread` no Store através de `add_model_values`,
sem nova serialização e sem recursão.

## Atualização

1. Substituir completamente a pasta `chatter_notifications`.
2. Apagar `__pycache__` antigos caso existam.
3. Reiniciar o Odoo.
4. Atualizar o módulo:
   `-u chatter_notifications`
5. Fazer `Ctrl + F5`.
6. Criar uma nova mensagem/menção numa tarefa e verificar a notificação.

## Versão 19.0.1.4.0

Adiciona notificações também quando uma mensagem manual do chatter é editada.

No Odoo 19, a edição de uma mensagem atualiza diretamente o registo
`mail.message`, sem voltar a executar `project.task.message_post()`. Esta versão
interceta alterações reais ao corpo da mensagem e volta a criar uma notificação
Inbox não lida para todos os seguidores internos ativos da tarefa, exceto o
utilizador que efetuou a edição.

A notificação é enviada pelo mecanismo nativo de Inbox/Bus do Odoo, pelo que os
browsers abertos recebem a atualização em tempo real.
