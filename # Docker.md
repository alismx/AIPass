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


## Git Workflow (inside the container)

The container is a separate user. It clones from your fork, not the main repo.

  ┌─────────────────────────────────┬──────────────────────────────────────────┐
  │            Command              │            What it does                   │
  ├─────────────────────────────────┼──────────────────────────────────────────┤
  │ git pull upstream main          │ Pull latest from AIOSAI/AIPass (source)  │
  ├─────────────────────────────────┼──────────────────────────────────────────┤
  │ git push origin main            │ Push to your fork (Input-X/AIPass)       │
  ├─────────────────────────────────┼──────────────────────────────────────────┤
  │ git remote -v                   │ Check which remotes are set              │
  ├─────────────────────────────────┼──────────────────────────────────────────┤
  │ git log --oneline -5            │ See recent commits                       │
  └─────────────────────────────────┴──────────────────────────────────────────┘

  Remotes:
    origin   = Input-X/AIPass   (your fork — push here)
    upstream = AIOSAI/AIPass    (main repo — pull from here)

  Typical flow:
    1. git pull upstream main        # Get latest changes
    2. Work on your code
    3. git add . && git commit -m "what you did"
    4. git push origin main          # Push to your fork

  Nothing you do in the container touches AIOSAI/AIPass directly.