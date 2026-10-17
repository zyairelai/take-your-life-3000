### Firefox Setup
- Go to `about:config`
- set `True` for `toolkit.tabbox.switchByScrolling`
- set `False` for `ui.key.menuAccessKeyFocuses`

### Sublime Text 
- Go to `Preferences` -> `Settings` and add the following:
```
{
	"update_check": false,
	"font": 14
}
```

### No Sudo Password Policy
```
sudo dpkg-reconfigure kali-grant-root
```

### Docker Setup
```
sudo apt update && sudo apt install -y ca-certificates curl gnupg zsh docker-compose-v2 docker.io
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

# Tmux
```
echo -e "set linenumbers" > .nanorc
echo -e "# Change the prefix key to C-a\nset -g prefix C-a\nunbind C-b\nbind C-a send-prefix\nset-option -g mouse on" > .tmux.conf
```

# ZSH Setup
```
sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
mv ~/.zshrc ~/.zshrc.bak
mv ~/.oh-my-zsh/lib/directories.zsh ~/.oh-my-zsh/lib/directories.zsh.bak
wget https://raw.githubusercontent.com/zyairelai/kali-rice/master/dotfiles/zsh/kali.zshrc -O ~/.zshrc
wget https://raw.githubusercontent.com/zyairelai/kali-rice/master/dotfiles/zsh/directories.zsh -O ~/.oh-my-zsh/lib/directories.zsh
wget https://raw.githubusercontent.com/zyairelai/kali-rice/master/dotfiles/zsh/kali.zsh-theme -O ~/.oh-my-zsh/custom/themes/kali.zsh-theme
```