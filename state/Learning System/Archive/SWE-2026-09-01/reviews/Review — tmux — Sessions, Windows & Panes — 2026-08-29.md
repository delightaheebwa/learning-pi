# Review — tmux — Sessions, Windows & Panes — 2026-08-29

- Track: SWE (Command-line Environment)
- Type: memory
- Last Q Type: definitional → asked discriminative
- Grade: PASS

## Question
Plain background job (`cmd &`) dies on disconnect unless nohup/disown. What does a tmux Session give you that the background job does not when the connection drops?

## Expected
A tmux Session is an independent workspace on the server, decoupled from the terminal — it survives detach/disconnect and logout; a plain bg job is a child of the terminal shell and gets SIGHUP-killed on close unless nohup/disown.

## Learner answer
Correct: tmux decouples from the local machine, job keeps running after SSH drop/logout; bg job gets kill signal on disconnect.

## Action
Interval advanced (memory +1). Next review 2026-09-12. Feynman: — (memory type).