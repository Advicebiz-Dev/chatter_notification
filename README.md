Project Chatter Follower Notifications

Módulo personalizado para Odoo 19.

Funcionalidades

Notifica os seguidores internos das tarefas através do Inbox do Odoo, mesmo que não estejam atribuídos à tarefa.

Notifica os seguidores quando uma mensagem do chatter é criada ou editada.

Exclui o autor da mensagem ou da edição das notificações.

Ignora mensagens técnicas e automáticas.

Atualiza as notificações em tempo real através do mecanismo nativo do Odoo.

Formato das notificações

As notificações apresentam o seguinte formato:

Cliente | Projeto | Tarefa

Se não existir cliente ou projeto, são apresentados apenas os elementos disponíveis.

O nome original da tarefa não é alterado.

Versão 19.0.1.4.0

Adiciona notificações para mensagens editadas.

Corrige o erro de recursão (RecursionError) da versão 19.0.1.3.0.

Mantém a compatibilidade com o sistema nativo de notificações do Odoo 19.

Atualização

Substituir a pasta chatter_notifications.

Reiniciar o Odoo.

Atualizar o módulo com -u chatter_notifications.

Atualizar o navegador (Ctrl + F5).

Testar a criação e edição de mensagens numa tarefa.
