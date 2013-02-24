Title:        Using PGP for SSH verification/authentication: What is Monkeysphere, and why should you care?
Author:       Etienne Perot <etienne (at) perot (dot) me>
Date:         2012-09-16
License:      CC-BY-3.0
ThumbnailUrl: monkeysphere.png

One of the issues with [SSH] is the lack of [public-key infrastructure]. This causes two kinds of potential problems.

## Fingerprint verification problem

Fingerprint verification is the technique SSH uses to check if it is connecting to the correct server, to ensure that the connection being not tampered with and not wiretappable.

In practice, this means that when you connect to a new SSH server, you're usually presented with something like this:

	:::console
	$ ssh perot.me
	The authenticity of host 'perot.me (2600:3c03::f03c:91ff:fe93:5318)' can't be established.
	ECDSA key fingerprint is 87:e2:c8:25:25:ee:a8:a6:ad:c9:2a:a5:2c:ae:8a:cf.
	Are you sure you want to continue connecting (yes/no)?

That bunch of random characters called the "fingerprint" is what SSH relies on to correctly authenticate to the server in the future. When you say "yes" to this prompt, SSH will save this fingerprint and the associated hostname in your `~/.ssh/known_hosts` so that in the future, SSH can check if the hostname still has the same fingerprint. If it does, then you're pretty safe. If it's not, here's what happens:

	:::console
	$ ssh perot.me
	@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
	@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
	Someone could be eavesdropping on you right now (man-in-the-middle attack)!
	It is also possible that a host key has just been changed.
	The fingerprint for the ECDSA key sent by the remote host is
	6c:78:41:0d:48:29:6c:ec:53:0f:66:04:02:53:02:49.
	Please contact your system administrator.
	Add correct host key in ~/.ssh/known_hosts to get rid of this message.
	Offending ECDSA key in ~/.ssh/known_hosts:linenumber
	ECDSA host key for localhost has changed and you have requested strict checking.
	Host key verification failed.

This scary message tells you that either the connection is being [man-in-the-middle]'d, or the server has been [rekeyed][Rekeying], which causes the fingerprint to change.

This model is informally called [TOFU] (Trust On First Use). It raises the following questions:

* How do you know for sure if the fingerprint is valid when you connect to a machine for the first time?
* When the fingerprint changes, how do you know if this happened because of a legit key change, or because the connection is being tampered with?

The SSH fingerprint model by itself does not solve these issues. To stay secure, you need to rely on a secure out-of-band channel to tell you the correct answer to both of these questions.

## Client authentication problem

**The second problem** is related to authentication (logging in to a server). By now you probably know that in order to authenticate to an SSH server with a key, you need to copy the public part of your SSH key (`~/.ssh/id_xxx.pub`) to the host's `authorized_keys` file. Then, the private part of your SSH key (`~/.ssh/id_xxx`) allows you to prove to the server that *you possess the private part* of the key that the server trusts the public part of. The SSH server *doesn't trust **you***, it trusts *whoever **owns the private part** of that key*. So what happens when your private key gets compromised, because you accidentally pasted it somewhere, or because your computer got exploited, or because you lost your laptop somewhere?

By then, you will probably have copied your public key in dozens or hundreds of accounts all around, and it can be quite painful to change every single one of them, let alone remember all the places where you've put it. And that's *assuming the attacker didn't already break into your servers* and deny you access from it.

This is not a big problem if you have one or two personal servers. It is a much bigger problem if you're managing a few dozens or hundreds of servers. The problem scales with the number of servers and accounts that you manage. However, the more servers you manage, the harder it becomes to change them or switch to a different solution. As such, it is better to take measures before the scope of the problem is prohibitively large.

**The goal of [the Monkeysphere project][Monkeysphere] is to address all of the aforementioned issues.** It is a system that extends [PGP] to other protocols such as SSH and HTTPS. The goal is to leverage PGP's [Web of trust] and use it for fingerprint-checking and authentication. This allows SSH fingerprint signing (to solve the fingerprint verification problem), and key signing/key revocation (to solve the authentication problem). The best part is that you don't need to get a patched version of OpenSSH or give up SSH-style key authentication to do it; Monkeysphere simply builds upon SSH, it doesn't remove any of its features.

Now that we've established why Monkeysphere is important, let's set it up.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This post assumes that you are already comfortable with SSH, and already have an SSH server running. It also assumes that you are comfortable with PGP, and already have generated a keypair with it, sitting comfortably in your keyring. If that's not the case, search around the Web, there are plenty of tutorials on how to do this for pretty much every operating system out there. It is also assumed that Monkeysphere is installed everywhere, through your favorite package manager.

Throughout this post, the following names will be used:

* **Cervo**: The server (machine), known on the Internet under the hostname `cervo.it-corp.com`
* **Dave Aldridge**: The sysadmin (human), with PGP key `dave@it-corp.com`
* **Demin**: The sysadmin's machine. Dave physically sits at its desk and manages other servers from this machine.
* **Joe Knaus**: The SSH user (human), with PGP key `joe@riseup.net`
* **Clint**: The client machine. Joe physically sits at its desk and wants to log in to `joe@cervo.it-corp.com` through SSH.

All commands are prefixed by a prompt containing `user@host`, indicating on which machine the command is meant to be run, and by who.

## Solving the fingerprint verification problem

There are three steps to making Cervo's fingerprint secure:

* Dave needs to sign Cervo's fingerprint
* Joe needs to set up his SSH client to use Monkeysphere
* Joe needs to trust the service key (by using the PGP trust model)

### Server-side: Signing the fingerprint

The first step is to create a PGP service key. It is a standard PGP key except that instead of identifying a human being, it identifies a service. In our case, it identifies the SSH service. Monkeysphere provides a handy function to do this in one shot:

	:::console
	root@cervo # monkeysphere-host import-key /etc/ssh/ssh_host_rsa_key ssh://cervo.it-corp.com

This command takes the server's SSH RSA key (from which the fingerprint can be derived) stored at `/etc/ssh/ssh_host_rsa_key`, and creates a new PGP service key identifying the service `ssh://cervo.it-corp.com`, which represents the SSH service on `cervo.it-corp.com`. The output looks like this:

	:::console
	ms: host key imported:
	pub   2048R/D9BA852B 2012-09-10
	uid                  ssh://cervo.it-corp.com
	OpenPGP fingerprint: 0A73F919251C7D6B579C214424F32D4FD9BA852B
	ssh fingerprint: 2048 89:e3:e7:3d:bd:ad:ef:f0:31:df:c7:50:42:99:64:54 (RSA)

This gives you the SSH fingerprint of the server, and the fingerprint of the PGP key which will allow you to identify it later on when you need to sign it.

The next step is to publish the key to a PGP keyserver. Again, Monkeysphere has a handy function for that:

	:::console
	root@cervo # monkeysphere-host publish-key

It will ask you if you are sure and will then send the key to a keyserver (the default is currently `pool.sks-keyservers.net`; this can be changed in the configuration files in `/etc/monkeysphere`).

Now we need to import the key on Dave's machine (Demin). Tihs may fail if you execute it instantly afterwards; wait a little bit for the keyserver to synchronize their keys between each other.

	:::console
	dave@demin $ gpg --recv-keys 0A73F919251C7D6B579C214424F32D4FD9BA852B

The large chain of characters is the OpenPGP fingerprint obtained from the host's `monkeysphere-host import-key` command. If you need to display that fingerprint again on the host because you forgot to write it down, you can use:

	:::console
	root@cervo # monkeysphere-host show-key

Once you have downloaded the right key, it's time to sign it:

	:::console
	dave@demin $ gpg --sign-key 0A73F919251C7D6B579C214424F32D4FD9BA852B

By doing this, you certify that you (Dave) believe that Cervo's SSH fingerprint is the one attached to this PGP key.

The last step is to publish your signature to the keyserver so that everyone can know about it:

	:::console
	dave@demin $ gpg --send-key 0A73F919251C7D6B579C214424F32D4FD9BA852B

You're done for the server side of things!

### Client-side: Checking the fingerprint

First, we need to set up Monkeysphere. On the client side, it's not as simple as installing a package. You need to use Monkeysphere as an SSH `ProxyCommand`, which allows Monkeysphere to do all its fancy stuff without you even having to notice it. To do this, simply add the following to your `~/.ssh/config`:

	:::console
	joe@clint $ $EDITOR ~/.ssh/config

~--~

	:::text
	# Add this at the end or in the existing "Host *" section
	Host *
	ProxyCommand monkeysphere ssh-proxycommand %h %p

If you already have a `Host *` section, then just add the line in it.

Next, we just need to run SSH:

	:::console
	joe@clint $ ssh cervo.it-corp.com

At this point, one of two possible things may happen. If you (Joe) don't trust the person (thus the key) who signed Cervo's SSH fingerprint, then you will see this:

	:::console
	joe@clint $ ssh cervo.it-corp.com
	-------------------- Monkeysphere warning -------------------
	Monkeysphere found OpenPGP keys for this hostname, but none had full validity.
	An OpenPGP key matching the ssh key offered by the host was found:
	
	pub   2048R/D9BA852B 2012-09-10
	uid       [ unknown] ssh://cervo.it-corp.com
	sig!3        D9CA862B 2012-09-10  ssh://cervo.it-corp.com
	RSA key fingerprint is 89:e3:e7:3d:bd:ad:ef:f0:31:df:c7:50:42:99:64:54.
	-------------------- ssh continues below --------------------
	The authenticity of host 'cervo.it-corp.com (<no hostip for proxy command>)' can't be established.
	ECDSA key fingerprint is 87:e2:c9:45:05:ef:ac:a6:4d:c9:2a:a5:2c:ae:8b:c3.
	Are you sure you want to continue connecting (yes/no)?

You are presented with the key that was found to match the service (`ssh://cervo.it-corp.com`), but it cannot be validated because PGP doesn't trust it. You have the option of blindly trusting it (as you would do if you were using regular SSH); or, you can establish a secure channel between the system administrator (Dave) and you (Joe), exchange PGP fingerprints, sign each other's key, etc. Do the same with other people who have already signed the service key, to be safer. Once the key is trusted, try to run SSH again, and you will see this:

	:::console
	joe@clint $ ssh cervo.it-corp.com
	joe@cervo $ # Success!

That's right: **you won't see anything**. The entire process is invisible. It doesn't need to be visible; you've already trusted Dave and others to correctly report SSH fingerprints, after all.

There is one last optional step: Sign the SSH service key yourself! This will make it easier for others to ssh into the server later, since the more signatures a key has, the bigger the network is, and thus the more likely that the service key will be trusted without further user intervention.

### Addendum: Re-keying a server

If you need to re-key a server (for example, if you wiped its hard drive completely, or if the host's private key got compromised), here is what you need to do.

First, if the host key was compromised (or even if it wasn't but you just want to be safe), add a signature revocation to the service key, in order to invalidate your signature from it:

	:::console
	dave@demin $ gpg --edit-key 0A73F919251C7D6B579C214424F32D4FD9BA852B
	gpg> revsig
	Create a revocation certificate for this signature? (y/N) y
	[...]

If you still have access to the host's private service key, you can also revoke the entire key (`revkey`). This will invalidate the entire key, as opposed to your signature.

Next, regenerate the host's private keys:

	:::console
	root@cervo # systemctl stop sshd
	root@cervo # rm /etc/ssh/ssh_host_*
	root@cervo # systemctl start sshd

`sshd` will generate some new keys as it starts. Once done, follow the same instructions as described in the "Signing the fingerprint" section and you're done.

## Solving the client authentication problem

This part is slightly more intrusive and involved than the first. It also needs to be done with care, because this affects which SSH keys are accepted by `sshd`. As such, a misstep here could lock you out of the server. To make sure this doesn't happen, keep a root session open to your server in the background, and work in a second session.

There are quite a few steps to making using PGP for SSH authentication:

* Declaring a PGP key as the "identity certifier" of the server (Cervo). The PGP key of clients trying to connect must be signed by the identity certifier, otherwise they will be denied access.
* Having the identity certifier sign the keys of the users allowed to log in
* Populating the server's `~/.monkeysphere/authorized_user_ids` files
* Setting up Monkeysphere to generate regular `authorized_keys` files out of those `~/.monkeysphere/authorized_user_ids`
* Setting up `sshd` to use those generated `authorized_keys` files
* Getting users to use their PGP key to log in

Ready? Let's go.

### Server-side: Setting up authentication

This is the tough, long part.

First, declare a PGP key as the "identity certifier" of the server. This key will then sign other keys to mark them as trusted. Usually, the identity certifier should be you, the server admin, since you effectively have that authority already through the use of regular `authorized_keys` files. To declare a PGP key as identity certifier, you must first find your own key's fingerprint:

	:::console
	dave@demin $ gpg --fingerprint dave@it-corp.com
	pub   4096R/85E1C5E2 2012-05-12
	      Key fingerprint = 5E2C 9641 5210 D512 F521  A997 F4FC 3BB4 85E1 C5E2
	uid                  Dave Aldridge <dave@it-corp.com>
	sub   4096R/85E1C5E2 2012-06-12

In the case above, your fingerprint would be `5E2C 9641 5210 D512 F521  A997 F4FC 3BB4 85E1 C5E2`. Now you must pass that to Monkeysphere on the server, which expects it as a straight sequence of characters (without spaces):

	:::console
	root@cervo # monkeysphere-authentication add-identity-certifier 5E2C96415210D512F521A997F4FC3BB485E1C5E2
	gpg: requesting key 85E1C5E2 from hkp server pool.sks-keyservers.net
	ms: key found:
	pub   4096R/85E1C5E2 2012-05-12
	      Key fingerprint = 5E2C 9641 5210 D512 F521  A997 F4FC 3BB4 85E1 C5E2
	uid                  Dave Aldridge <dave@it-corp.com>
	sub   4096R/85E1C5E2 2012-06-12
	Are you sure you want to add the above key as a certifier of users on this system? (Y/n) Y
	ms: Identity certifier added.

The next step is to go sign the keys of all the users that have access to one or more accounts on the system, if you haven't already done so. Hopefully you should already know how to do that by now, but just as a reminder:

	:::console
	dave@demin $ gpg --sign-key (fingerprint of the key to sign) # Signs the key
	dave@demin $ gpg --send-key (fingerprint of the key to sign) # Publishes your signature on the keyserver

Repeat the process for everyone on your system who has a PGP key. For those who don't, proceed to slap them on the face, and then ask them to create one. If they still refuse, that's okay, they can still use their regular SSH keys as if nothing had happened, although they won't benefit from Monkeysphere and your server will be vulnerable if their key gets compromised (just like it used to be).

Now we need to populate the server's `~/.monkeysphere/authorized_user_ids` files. These act much like `~/.ssh/authorized_keys` files do; every account that can be logged into through SSH has one of those, and it contains a list of public keys; one per line. In Monkeysphere, `~/.monkeysphere/authorized_user_ids` files are simply a list of PGP identities; they are **not fingerprints**, they are **not key IDs**, or anything complicated and unreadable like that. They simply contain this:

	:::console
	root@cervo # $EDITOR /home/joe/.monkeysphere/authorized_user_ids

~--~

	:::text
	Dave Aldridge <dave@it-corp.com>
	Joe Knaus <joe@riseup.net>

That's it! This file indicates that both Dave and Joe can log in to this account through SSH. It's a list of humans, not a lot of cryptic garbage. As such, it's extremely readable and easy to maintain, unlike the long and cryptic `authorized_keys` files that only sometimes have a bit of optional identifying information at the end of the line. If you're not sure what the PGP identity of a key is, you can do the following:

	:::console
	dave@demin $ gpg --list-keys

Find the key in there, and look for the line beginning by `uid` that follows it. For example:

	:::console
	dave@demin $ gpg --list-keys
	[...]
	pub   4096R/85E1C5E2 2012-05-12
	uid                  Dave Aldridge <dave@it-corp.com> # This is the identity
	# (There may be more than one identity.)
	sub   4096R/85E1C5E2 2012-06-12
	[...]

Now, we need to have Monkeysphere use these `authorized_user_ids` files and generate SSH-style `authorized_keys` files out of them. What Monkeysphere will do is search the keyserver for keys matching each line of the `authorized_user_ids` file, check if any matching key has been signed by the identity certifier declared earlier, and if it does then it will add the SSH RSA key in the `authorized_keys` file, giving them access to the account.

To do this, just add an entry in `/etc/cron.daily` or so:

	:::console
	root@cervo # $EDITOR /etc/cron.daily/monkeysphere-update-users

~--~

	:::bash
	#!/bin/sh
	
	/usr/sbin/monkeysphere-authentication update-users

Don't forget to make it executable...

	:::console
	root@cervo # chmod +x /etc/cron.daily/monkeysphere-update-users

You should also run that command right now if you don't want to wait a day:

	:::console
	root@cervo # monkeysphere-authentication update-users

This will create `authorized_keys` files inside `/var/lib/monkeysphere/authorized_keys/` for all accounts that have a `~/.monkeysphere/authorized_user_ids` or a `~/.ssh/authorized_keys` file or both. It will collect RSA keys from the keyserver as described above, and *it will concatenate the result with the user's **existing***&nbsp;`~/.ssh/authorized_keys` file. It does this in order to not break your existing setup (SSH keys that are already authorized through `~/.ssh/authorized_keys` will *continue to work*), and in order for you to continue supporting users that don't have a PGP key or who for some reason don't want to use Monkeysphere. The fact that Monkeysphere does this is a good feature, but it does mean that you will need to clean up existing `~/.ssh/authorized_keys` files and *remove* SSH keys that belong to the users who have made the switch to Monkeysphere. Thankfully, you should only need to do this once. Once you are done, you should re-generate the `authorized_keys` files again:

	:::console
	root@cervo # monkeysphere-authentication update-users

Like I mentioned, the generated `authorized_keys` files are stored in `/var/lib/monkeysphere/authorized_keys/`, so that they don't overwrite your existing `~/.ssh/authorized_keys` and so that they are not visible to each user account. The flip side of that is that now you need to tell `sshd` to use these files instead of the usual `~/.ssh/authorized_keys`. To do this, edit `/etc/ssh/sshd_config`:

	:::console
	root@cervo # $EDITOR /etc/ssh/sshd_config

~--~

	:::text
	# Comment out existing "AuthorizedKeysFile" lines like this:
	#AuthorizedKeysFile      .ssh/authorized_keys
	
	# Add this somewhere in the file:
	AuthorizedKeysFile /var/lib/monkeysphere/authorized_keys/%u

This tells `sshd` to go look into `/var/lib/monkeysphere/authorized_keys/someuser` instead of `/home/someuser/.ssh/authorized_keys`.

Now, the scary part: You need to restart `sshd` so that your configuration changes are applied. First, make sure that Monkeysphere successfully generated the `authorized_keys` files:

	:::console
	root@cervo # ls /var/lib/monkeysphere/authorized_keys
	dave joe otheruser1 otheruser2 ...
	root@cervo # cat /var/lib/monkeysphere/authorized_keys/dave
	ssh-rsa AAAAB[...]X3ZQ== MonkeySphere2012-09-15T23:24:50 Dave Aldridge <dave@it-corp.com>

If everything looks good (as it does above), then restart sshd:

	:::console
	root@cervo # systemctl restart sshd

Before you can try it out, however, we still need to set up the client side of things. Thankfully, this is very easy.

### Client-side: Using a PGP key to log in

First, make sure you have an ssh agent running:

	:::console
	joe@clint $ ssh-add

If you didn't have an `ssh-agent` running, this command will complain about it. If it does, then start one (your desktop environment or your shell probably has an option for that). Then, ask Monkeysphere to populate it using your PGP key:

	:::console
	joe@clint $ monkeysphere subkey-to-ssh-agent joe@riseup.net

This will ask for the passphrase of your PGP key and will load the identity into your `ssh-agent`.

That's it! You should now be able to ssh into things:

	:::console
	joe@clint $ ssh cervo.it-corp.com
	joe@cervo $ # Success!

### Addendum: Automatic identity loading

Loading the identity into the `ssh-agent` can be a pain, since it asks for a passphrase and all. There is a way to automate it. This will require storing your PGP key passphrase on your hard drive, so of course you should only do this if you use [full disk encryption], or at least encryption on the files in the directory you're about to create. Let's put all of that into `~/.monkeysphere-automate` to keep things clean, and keep the permissions locked down so that only our account can touch things in it.

	:::console
	joe@clint $ mkdir ~/.monkeysphere-automate
	joe@clint $ chmod 700 ~/.monkeysphere-automate
	joe@clint $ cd ~/.monkeysphere-automate
	joe@clint [~/.monkeysphere-automate] $ 

First, you need to create a little script to replace `ssh-askpass` (the program that Monkeysphere uses to ask you the passphrase).

	:::console
	joe@clint [~/.monkeysphere-automate] $ $EDITOR populate-pass.sh

~--~

	:::bash
	#!/bin/sh
	
	echo 'my top secret passphrase'

Make it executable and readable only by you:

	:::console
	joe@clint [~/.monkeysphere-automate] $ chmod 700 populate-pass.sh

Then, we need to tell Monkeysphere which key to load. To do that, we need to find out the fingerprint of the **subkey** of the PGP key that you wish to authenticate with. Indeed, it's with the subkey that you authenticate. For the main user-facing functions of Monkeysphere, this is done automatically when necessary, but for this operation, Monkeysphere only lets you specify the fingerprint of the subkey. To do that, do a `--list-key --fingerprint --fingerprint` on your PGP key. You do need to specify `--fingerprint`&nbsp;**twice**. This tells gpg to print the both fingerprint of the main key and subkeys.

	:::console
	joe@clint [~/.monkeysphere-automate] $ gpg --list-key --fingerprint --fingerprint joe@riseup.net
	pub   4096R/5E239C51 2012-05-12
	      Key fingerprint = 96CD 8013 541D2 A706 C951  05F6 BB81 96F4 5E23 9C51
	uid                  Joe Knauss <joe@riseup.net>
	sub   4096R/DF8506B1 2012-05-12
	      Key fingerprint = 0652 CFF3 5E64 18E6 657A  C172 85E1 5CA0 DF85 06B1

It's the last line that we're interested in. It is the fingerprint of the subkey. Again, Monkeysphere expects this as a sequence of characters without spaces, so remove them. Now, we can create the actual script to load the identity:

	:::console
	joe@clint [~/.monkeysphere-automate] $ $EDITOR load-identity.sh

~--~

	:::bash
	#!/usr/bin/env bash
	
	SSH_ASKPASS="$HOME/.monkeysphere-automate/populate-pass.sh" MONKEYSPHERE_SUBKEYS_FOR_AGENT=0652CFF35E6418E6657AC17285E15CA0DF8506B1 monkeysphere subkey-to-ssh-agent

Make it executable and readable only by you:

	:::console
	joe@clint [~/.monkeysphere-automate] $ chmod 700 load-identity.sh

Now, just add `/home/joe/.monkeysphere-automate/load-identity.sh` to your list of startup scripts and you should be set. This will only work if you have `ssh-agent` also being spawned on startup, and it must be spawned before this script is invoked.

[SSH]: https://en.wikipedia.org/wiki/Secure_Shell
[public-key infrastructure]: https://en.wikipedia.org/wiki/Public_key_infrastructure
[TOFU]: https://en.wikipedia.org/wiki/User:Dotdotike/Trust_Upon_First_Use
[man-in-the-middle]: https://en.wikipedia.org/wiki/Man-in-the-middle_attack
[Rekeying]: https://en.wikipedia.org/wiki/Rekeying
[Monkeysphere]: http://web.monkeysphere.info/
[PGP]: https://en.wikipedia.org/wiki/Pretty_Good_Privacy
[Web of trust]: https://en.wikipedia.org/wiki/Web_of_trust
[full disk encryption]: https://en.wikipedia.org/wiki/Disk_encryption