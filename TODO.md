The tool should be able to create `systemd.netdev(5)` configuration files
to support systems based on `systemd-networkd(8)`.

By default, these would be created in the volatile directory, `/run/systemd/network/`.

Example:

```
[NetDev]
Name=wg0
Kind=wireguard
Description=Mullvad VPN

[WireGuard]
PrivateKeyFile=/path/to/unix.sock[et]

[WireGuardPeer]
PublicKey=RDf+LSpeEre7YEIKaxg+wbpsNV7du+ktR99uBEtIiCA=
AllowedIPs=0.0.0.0/0
AllowedIPs=::/0
Endpoint=wireguard.example.com:51820
```

By specifying `PrivateKeyFile` in combination with a UNIX socket, argbigga itself doesn't need access to the WireGuard key.

```
[Match]
Name=wg0

[Network]
Address=<ipv4 addr>/32
Address=<ipv6 addr>/128

[WireGuard]
PrivateKeyFile=/path/to/unix.sock[et]

[WireGuardPeer]
PublicKey=RDf+LSpeEre7YEIKaxg+wbpsNV7du+ktR99uBEtIiCA=
AllowedIPs=0.0.0.0/0
AllowedIPs=::/0
Endpoint=wireguard.example.com:51820
```
