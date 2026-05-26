sudo cp -f gps_launcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gps_launcher.service
sudo systemctl start gps_launcher.service