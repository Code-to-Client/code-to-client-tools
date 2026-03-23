# Projects commands

## cd (dir)
> Open a shell in a project folder. dir: server, client, form, bookkeeping, business, or any folder name.

```bash
case "${dir}" in
  server)   target="tracker-server" ;;
  client)   target="tracker-client" ;;
  filler)     target="autofiller" ;;
esac
cd "${target}" && exec ${SHELL:-bash}
```