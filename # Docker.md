# Docker


Docker stores images at /var/lib/docker/ (managed by the Docker daemon). You don't interact with it directly — Docker
   handles the layers.                                                                                                 
                                                                                                                       
  Your cheat sheet:                            
                                                                                                                       
  ┌────────────────────────────┬───────────────────────┐ 
  │          Command           │     What it does      │
  ├────────────────────────────┼───────────────────────┤
  │ docker start aipass-vscode │ Resume container      │
  ├────────────────────────────┼───────────────────────┤
  │ docker stop aipass-vscode  │ Pause container       │
  ├────────────────────────────┼───────────────────────┤
  │ docker images              │ List all images       │
  ├────────────────────────────┼───────────────────────┤
  │ docker ps -a               │ List all containers   │
  ├────────────────────────────┼───────────────────────┤
  │ docker system df           │ Disk usage            │
  ├────────────────────────────┼───────────────────────┤
  │ docker system prune        │ Clean up unused stuff │
  └────────────────────────────┴───────────────────────┘

  The aipass-test image (~260MB) stays until you docker rmi aipass-test. The container stays until you docker rm it.
  Both survive reboots.