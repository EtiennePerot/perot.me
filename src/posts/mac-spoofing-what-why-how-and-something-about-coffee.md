Title:        MAC spoofing: What, why, how, and something about coffee
Author:       Etienne Perot <etienne (at) perot (dot) me>
Date:         2013-01-22
License:      CC-BY-3.0
ThumbnailUrl: https://github.com/EtiennePerot/macchiato

[MAC addresses][MAC address] are a unique identifier associated to every network interface, wired or wireless. They are used to identify devices on a physical network.

Usually, a network interface comes with a fixed MAC address called the *burned-in address*. This address cannot be changed, as it is stored in the interface's hardware itself. Because of their fixed nature, they make it pretty easy to use for tracking purposes. This has some some pretty useful applications, such as being used as the matching criterion for a [DHCP] server to give a static IP address to a given device, or in order to target a "dormant" interface as required for [Wake-on-LAN].

[MAC spoofing] is the technique to effectively change the MAC address that your network interface appears to have. It doesn't change the burned-in address, it merely changes what other devices think your interface's MAC address is. It can be used for some legitimate and not-always-legitimate purposes:

* Appearing as a legitimate device on a network which employs [MAC address whitelisting] (useful when your last network interface dies, and for [certain types of network attacks][ARP Request Replay Attack])
* Avoiding tracking: Different MAC addresses means no device on the network can tell if it has already seen this device on this network before, or on another network. For example, Starbucks may wish to maintain a list of all MAC addresses accessing their WiFi access points and use this information to figure out someone's movements or simply to identify who their best customer is (or at least which one is *that guy* always hogging all the bandwidth)
* Appearing as a different device to a network you've previously been on (hey, remember those "time-limited" free WiFi access points at the airport?)
* Avoiding profiling: The first three bytes of the MAC address identify the manufacturer of the device. Thus, the burned-in address gives away which company made the chip. Sometimes that's not important, but perhaps a hardware exploit exists in all network interfaces manufactured by $MANUFACTURER, thus changing your MAC address gives you a bit of security by obscurity. Or, more mundanely, perhaps you don't want a thief to be able to see that you have a shiny, new, and *very expensive* iThingy at your house simply by standing outside and looking all the MAC addresses broadcasted by all your WiFi devices.
* [Bypassing futile roadblocks][Errata Security - I conceal my identity the same way Aaron was indicted for], and [unjustly getting prosecuted to death][EFF - Aaron Swartz's Death] over it
* Wireless access points use MAC spoofing in order to provide multiple wireless networks with a single wireless interface. Recent routers often have this "guest network" feature which, when turned on, makes your router show up twice in the list of available access points: The regular network, and the guest network. This is a good thing, as it gives you some network-level isolation between machines. This way, even if your guests don't practice healthy security practices on their computing devices, at least they won't spread any nasty stuff through your LAN.

Interestingly, while MAC addresses have thus far been limited in terms of tracking potential due to being confined to one's local network, this is about to change with [IPv6]. One of IPv6's addressing models, [stateless address autoconfiguration][Stateless address autoconfiguration], allows a device to acquire an address for itself by taking the 64-bit prefix of the network it is on, and using the 48-bit MAC address of its network interface to determine the value of the remaining 64 bits. The consequence of this scheme is that any website you connect to can figure out your MAC address from nothing but your IPv6 address. (More on that later.)

As you can see, there are many reasons as to one would want to spoof their MAC address. So how do we get in on the action?

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To randomize MAC addresses, we will be using an aptly-named program called [GNU MAC Changer], available on most distributions under the `macchanger` package. Some distributions have a different package for the [Debian version of `macchanger`][Debian macchanger package], which includes some pretty important fixes such as an updated list of manufacturers, more granularity in the time value used for the random number generator's seed. On Arch, that package is known on the AUR as [`macchanger-debian`][macchanger-debian on the AUR]. This guide uses the output from the Debian version. There is also a GTK interface to it called [`macchanger-gtk`][macchanger-gtk], but we will not be using this. This guide also assumes that you are using [systemd] as init daemon.

## Step 1: Preliminary data gathering

In order to spoof a network interface's MAC address, we first need to know which interface we should spoof the MAC address of. Thus, we should check out our list of network interfaces. There are various ways to figure this out (`ifconfig`, `ip`, `airmon-ng`, tab-completion on some commands, etc.). Here, we will use `ip` because it lists some other information we are interested in:

	:::console
	$ sudo ip addr
	1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN 
	    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
	    inet 127.0.0.1/8 scope host lo
	    inet6 ::1/128 scope host 
	       valid_lft forever preferred_lft forever
	2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP qlen 1000
	    link/ether xx:xx:xx:xx:xx:xx brd ff:ff:ff:ff:ff:ff
	    inet .../xx brd ... scope global wired0
	    inet6 .../xx scope link 
	       valid_lft forever preferred_lft forever
	4: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN qlen 100
	    link/none 
	    inet ../xx brd ... scope global tun0
	5: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	    link/ether xx:xx:xx:xx:xx:xx brd ff:ff:ff:ff:ff:ff
	    inet .../xx brd ... scope global wlan0
	    inet6 .../xx scope link 
	       valid_lft forever preferred_lft forever

In the above example, 4 interfaces have shown up: `lo`, `eth0`, `tun0`, and `wlan0`. The output also shows your current MAC address (shown as `xx:xx:xx:xx:xx:xx` above) and your current IPv4 and IPv6 addresses for each interface. Go through each interface, determine what it's here for, and decide which ones you want to perform MAC spoofing on. In the above example:

* `lo` is the local loopback interface. It is used for internal traffic, such as when you run a "local web application" which is simply a process that binds to `localhost:someport` and lets you connect to it through your browser. This interface has the MAC address `00:00:00:00:00:00` because it is not a real network interface.
* `eth0` is the actual Ethernet network interface of the machine (hence "`eth`"). You probably do want to spoof the MAC address on this one. Its current MAC address, which should currently correspond to your burned-in address, is shown on the second line ("`link/ether xx:xx:xx:xx:xx:xx`")
* `tun0` is the virtual interface that would be created by [OpenVPN]. As it is not a physical network interface, it doesn't have a MAC address.
* `wlan0` is a USB WiFi adapter plugged into the computer. It shows as a physical network interface with its own MAC address. You probably do want to spoof its MAC address: since it's a wireless interface, it will likely travel a lot and connect to a variety of access points, so it is the type of interface that would benefit the most from MAC spoofing.

Other types of interfaces can appear, such as `athX` (Atheros chips), `vboxnetX` (virtual network interfaces created by [VirtualBox]), etc.

### Step 1.5 (optional): Renaming network interfaces

If you have a Broadcom chip, read this section. If not, feel free to read it or not. It may prove interesting and/or useful anyway.

Some Broadcom drivers have the very annoying tendency to:

* Assign a name like `ethX` to the *wireless* network interface
* Inconsistently assign interface names (one boot you have `eth0` being the Ethernet interface and `eth1` being the wireless interface, the next boot you have `eth0` being the wireless interface and `eth1` being the Ethernet interface)

This is not only annoying, it also means that if you decide to use MAC spoofing for one of the two interfaces, you may actually be spoofing the MAC address of the wrong interface. This can be fixed by renaming interfaces so that their name stays consistent. And while we're at it, let's not call a wireless interface `ethX`. To do this, we are going to write [udev] rules.

First, figure out the MAC address of both interfaces and determines which one belongs to which physical interface.

Then, create a file in `/etc/udev/rules.d/` that looks like this:

	:::console
	$ sudo $EDITOR /etc/udev/rules.d/10-network-interface-names.rules
	SUBSYSTEM=="net", ATTR{address}=="00:11:22:33:44:55", NAME="wired"
	SUBSYSTEM=="net", ATTR{address}=="66:77:88:99:AA:BB", NAME="wifi"

Each line contains the MAC address of the network interface, along with the desired name it should have. This name can be anything descriptive to you, just don't use fancy characters. You will need to reboot for the changes to take place. I suggest you do it now, because the rest of the guide requires you to type the correct network interface names.

**Bonus**: You could rename the OpenVPN interface as well, even though it doesn't have a MAC address:

	:::console
	$ sudo $EDITOR /etc/udev/rules.d/10-network-interface-names.rules
	SUBSYSTEM=="net", ATTR{address}=="00:11:22:33:44:55", NAME="wired"
	SUBSYSTEM=="net", ATTR{address}=="66:77:88:99:AA:BB", NAME="wifi"
	SUBSYSTEM=="net", KERNEL=="tun0", NAME="vpn"

Rebooted? Good! Let's continue.

## Step 2: Installing the package

This one is a piece of cake. Either install `macchanger` or the Debian variant of it, using your favorite package manager (in this case, `pacman`/[`yaourt`][Yaourt package manager]).

	:::console
	$ yaourt -S macchanger-debian # Debian version
	or
	$ sudo pacman -S macchanger # Non-debian version

## Step 3: Initial spoof

We'll assume that the interface you want to perform MAC spoofing on is called `wlan0` from this point on. Chances are you are currently still using its burned-in address. Let's check it out:

	:::console
	$ macchanger wlan0
	Permanent MAC: 6c:fd:b9:6f:c8:d2 (Proware Technologies Co Ltd.)
	Current   MAC: 6c:fd:b9:6f:c8:d2 (Proware Technologies Co Ltd.)

Let's fix that. First, let's bring the interface down so that the network manager doesn't step on our toes (warning: *This will disconnect you* if you are currently using this interface to access the Internet):

	:::console
	$ sudo ip link set wlan0 down

Now we can ask `macchanger` to assign a randomized MAC address to the device:

	:::console
	$ sudo macchanger -r wlan0
	Permanent MAC: 6c:fd:b9:6f:c8:d2 (Proware Technologies Co Ltd.)
	Current   MAC: 6c:fd:b9:6f:c8:d2 (Proware Technologies Co Ltd.)
	New       MAC: 3e:72:02:04:0b:3d (unknown)

The output is a bit ambiguous; the "Current MAC" line seems to say that the address is still the same. The actual MAC address of the interface is still the one on the last line, however. You can confirm this by simply running `macchanger wlan0` again. Then we can bring the interface back up:

	:::console
	$ sudo ip link set wlan0 up

Now you should be able to use the network interface as normal, with its MAC address spoofed as `3e:72:02:04:0b:3d`. But wait! That address is weird. `macchanger` said it was "unknown", whereas it could determine which manufacturer the original MAC address belonged to. For that, it uses the first 3 bytes of the MAC address, which are attributed to a given organization. For the modest sum of [US$1,885 given to the IEEE][IEEE-SA OUI registration], you can apply to be given your own 3-bytes sequence (called the [Organizationally Unique Identifier, OUI][Organizationally Unique Identifier]) and proudly appear in the [IEEE's public OUI registry]. The 3-bytes sequence of the randomized MAC address `macchanger` chose above, `3e-72-02`, is not registered, thus it shows as unknown. This may be good enough (if so, then skip ahead to the next step), but it is a dead giveaway that you are using MAC spoofing to any person or any software watching the MAC address list of the network. This can be used as a criterion for denying you access to the network, for example. To this end, `macchanger` provides the `-A` switch, which makes the first 3 bytes be taken from `macchanger`'s internal list of manufacturers. You can view this list using:

	:::console
	$ macchanger -l

The Debian version of `macchanger` has a much bigger list. Using the `-A` switch makes it pick the OUI prefix from this list, resulting in a legitimate-looking MAC address:

	:::console
	$ sudo ip link set wlan0 down
	$ sudo macchanger -A wlan0
	Permanent MAC: 6c:fd:b9:6f:c8:d2 (Proware Technologies Co Ltd.)
	Current   MAC: 3e:72:02:04:0b:3d (unknown)
	New       MAC: 00:1d:ab:12:84:81 (Swissqual License Ag)
	$ sudo ip link set wlan0 up

That's an improvement, but it's still kinda fishy. You can try running the above commands multiple times to cycle through manufacturers and you'll mostly see Chinese companies you've rarely heard of. Thus, a lot of the time, your device will appear to have a MAC address from uncommon manufacturers, by which a human may still deduce that you are spoofing your MAC address. Again, that may be good enough (if so, then skip ahead to the next step). However, we can still do better by reducing the subset of manufacturers macchanger uses to a small list of "known-popular" manufacturers. This way, it becomes harder for others to figure out that the MAC address is spoofed. I have created such a project, affectionately named [macchiato] (MAC Changer Hiding Identification And Transposing OUIs). There is an Arch package for it that you can install:

	:::console
	$ yaourt -S macchiato-git

Or, if you're on another systemd-using distribution and you want to install it from scratch:

	:::console
	$ git clone git://perot.me/macchiato
	$ sudo macchiato/install-systemd-service.sh

Now there is some configuration to do. The procedure above (whichever one you used) created a directory called `/etc/macchiato.d/`. In it, you need to create one configuration file per interface you wish to perform MAC spoofing for. A sample configuration file is provided at `/etc/macchiato.d/sample.sh.example`. It looks like this (the actual file also has in-depth comments):

	:::bash
	ouiList=(
		wireless_laptop
		wireless_usb
	)
	
	ouiBlacklist=(
		00:26:bb # Apple, Inc.
	)

The names in the `ouiList` entry refer to files in `/usr/share/macchiato/oui/` if you installed the Arch package, or `/wherever/you/cloned/it/macchiato/oui/` if you cloned it yourself. Each of these files contains a list of common OUI prefixes corresponding to a certain category of network interfaces. For example, `wireless_laptop` correspond to OUI prefixes of onboard wireless chips found within laptop computers. If you have a "common" computer, then feel free to post a comment below listing your OUI prefixes of your network adapters. make sure to specify which category of network adapter each OUI prefix corresponds to. Or you can send a pull request on the [macchiato GitHub repository][macchiato on GitHub]. Or [the Bitbucket one][macchiato on Bitbucket]. Whichever you prefer.

Create one such configuration file for each network interface (for example, to spoof `wlan0`'s MAC address, create `/etc/macchiato.d/wlan0.sh`).

Once all of that is done, run the service to see if everything works:

	:::console
	$ sudo systemctl start macchiato

You don't need to bring the interface `up` or `down` manually; it should handle that for you. If `systemctl` yells at you, then there's probably a configuration error of some kind. Check out the service status:

	:::console
	$ sudo systemctl status macchiato

It will tell you why the service can't start. Once you do get it working, check out if the MAC address has properly changed according to your tastes:

	:::console
	$ macchanger wlan0

All good? Then it's time to...

## Step 4: Make it start on boot

If you followed step 3 all the way up to the end and installed `macchiato`, then you're almost done! You just need to enable the service:

	:::console
	$ sudo systemctl enable macchiato

If you haven't installed macchiato, then it isn't much more difficult. You just need to write a systemd service file to do the work:

	:::console
	$ sudo $EDITOR /etc/systemd/system/macspoof.service

<!-- Hacky comment to make markdown split this into two code blocks -->

	:::ini
	[Unit]
	Description=MAC address spoofing
	Before=NetworkManager.service dhcpcd.service dhcpcd@.service netcfg.service netcfg@.service wicd.service
	
	[Service]
	Type=oneshot
	ExecStart=/usr/bin/macchanger -A wlan0
	# Need to spoof another interface? Just add another ExecStart line:
	ExecStart=/usr/bin/macchanger -A eth0
	
	[Install]
	WantedBy=network.target

There's a bunch of network managers up there in the `Before` line. You don't need all of them, obviously, you just need the one you use. It doesn't hurt to leave them all there though; systemd will figure things out. Just need to enable it:

	$ sudo systemctl enable macspoof

You're done! You may want to reboot and check `macchanger wlan0` once again just to make sure everything works.

## Bonus: Enable [IPv6 Privacy Extensions][Privacy Extensions for Stateless Address Autoconfiguration in IPv6]

Remember that thing about IPv6 [stateless address autoconfiguration][Stateless address autoconfiguration] from earlier? There exists some (optional) [privacy extensions to the scheme][Privacy Extensions for Stateless Address Autoconfiguration in IPv6], which are enabled by default in some distributions such as [Ubuntu][IPv6 Privacy Extensions enabled by default in Ubuntu], as well as in some other obscure operating systems known by the appealing monikers of "[Microsoft Windows][IPv6 Privacy Extensions enabled by default in Windows Vista]" (since Vista) and "[OS X][IPv6 Privacy Extensions enabled by default in OS X]" (since 10.7).

An effective way of mitigating the privacy risk of MAC addresses embedded in IPv6 addresses, regardless of whether these privacy extensions are enabled or not, is simply to not use your device's burned-in address: that's MAC spoofing. But while you're at it tweaking your system, you may might as well enable them anyway, right? This is done by setting some kernel parameters. Drop a new file in `/etc/sysctl.d/`:

	$ sudo $EDITOR /etc/sysctl.d/10-ipv6-privacy-extensions.conf
	net.ipv6.conf.all.use_tempaddr = 2
	net.ipv6.conf.default.use_tempaddr = 2
	
	# For each interface, add a line like this:
	# net.ipv6.conf.<interface name>.use_tempaddr = 2
	# For example:
	net.ipv6.conf.eth0.use_tempaddr = 2
	net.ipv6.conf.wlan0.use_tempaddr = 2

Minor note: On Ubuntu or Ubuntu-based distributions, [a patch has already been applied][Ubuntu - Matt's Blog - Enabling IPv6 Privacy Addresses] to your kernel which makes [changes to `net.ipv6.conf.all.use_tempaddr` trickle down to all network interfaces][Ubuntu kernel-team mailing list PATCH - IPv6: make the net.ipv6.conf.all.use_tempaddr sysctl propagate to interface settings]. As such, with those kernels, only the first 2 lines of the above configuration file are necessary. Still, it doesn't hurt to add the rest anyway.

Happy spoofing.

[MAC address]: https://en.wikipedia.org/wiki/MAC_address
[DHCP]: https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol
[Wake-on-LAN]: https://en.wikipedia.org/wiki/Wake-on-LAN
[MAC spoofing]: https://en.wikipedia.org/wiki/MAC_spoofing
[MAC address whitelisting]: https://en.wikipedia.org/wiki/Whitelist#LAN_whitelists
[ARP Request Replay Attack]: http://www.aircrack-ng.org/doku.php?id=arp-request_reinjection
[Errata Security - I conceal my identity the same way Aaron was indicted for]: http://erratasec.blogspot.com/2013/01/i-conceal-my-identity-same-way-aaron.html
[EFF - Aaron Swartz's Death]: https://www.eff.org/deeplinks/2013/01/aaron-swartz-fix-draconian-computer-crime-law
[IPv6]: https://en.wikipedia.org/wiki/IPv6
[Stateless address autoconfiguration]: https://en.wikipedia.org/wiki/IPv6_address#Stateless_address_autoconfiguration
[Privacy Extensions for Stateless Address Autoconfiguration in IPv6]: https://www.ietf.org/rfc/rfc3041.txt
[IPv6 Privacy Extensions enabled by default in Ubuntu]: https://bugs.launchpad.net/ubuntu/+source/procps/+bug/176125
[IPv6 Privacy Extensions enabled by default in Windows Vista]: http://ipv6int.net/systems/windows_vista-ipv6.html#privacy
[IPv6 Privacy Extensions enabled by default in OS X]: https://wikispaces.psu.edu/display/ipv6/IPv6+on+OS+X
[GNU MAC Changer]: http://directory.fsf.org/wiki/GNU_MAC_Changer
[Debian macchanger package]: http://packages.debian.org/search?keywords=macchanger
[macchanger-debian on the AUR]: https://aur.archlinux.org/packages/macchanger-debian
[macchanger-gtk]: https://aur.archlinux.org/packages/macchanger-gtk
[systemd]: https://en.wikipedia.org/wiki/Systemd
[OpenVPN]: https://openvpn.net/
[VirtualBox]: https://www.virtualbox.org/
[udev]: https://en.wikipedia.org/wiki/Udev
[Yaourt package manager]: https://wiki.archlinux.org/index.php/Yaourt
[IEEE-SA OUI registration]: https://standards.ieee.org/develop/regauth/oui/
[Organizationally Unique Identifier]: https://en.wikipedia.org/wiki/Organizationally_Unique_Identifier
[IEEE's public OUI registry]: https://standards.ieee.org/develop/regauth/oui/oui.txt
[macchiato]: https://github.com/EtiennePerot/macchiato
[macchiato on GitHub]: https://github.com/EtiennePerot/macchiato
[macchiato on BitBucket]: https://bitbucket.org/EtiennePerot/macchiato
[Ubuntu - Matt's Blog - Enabling IPv6 Privacy Addresses]: http://blog.cyphermox.net/2011/12/enabling-ipv6-privacy-addresses.html
[Ubuntu kernel-team mailing list PATCH - IPv6: make the net.ipv6.conf.all.use_tempaddr sysctl propagate to interface settings]: https://lists.ubuntu.com/archives/kernel-team/2011-December/018284.html