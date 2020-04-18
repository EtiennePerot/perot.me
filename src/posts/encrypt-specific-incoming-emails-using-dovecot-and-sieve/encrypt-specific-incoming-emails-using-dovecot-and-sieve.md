Title:        Encrypt specific incoming emails using Dovecot and Sieve
Author:       Etienne Perot <etienne (at) perot (dot) me>
Date:         2012-07-14
License:      CC-BY-3.0
ThumbnailUrl: diagram.png

After reliability, security is perhaps the second most important aspect of a mail server. I was looking for solutions to encrypt all incoming emails (that were not already encrypted) with [my PGP key] as soon as they arrive on my mail server. This way, even if an attacker gains access to the system, (s)he will not be able to read the contents of emails that are already stored on disk.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There already exists [a solution to this][Grepular - Automatically Encrypting all Incoming Email]; however, this in order to encrypt incoming emails (that are not already encrypted) as soon as they are received, on the server side. However, this guide is for [Exim] only, and I wanted a solution that worked with my setup ([Postfix] and [Dovecot]).

It is possible to achieve using Postfix only. The [GPG-Mailgate] project does just that. However, it does not appear to be well-maintained, and looking at [its issues list][GPG-Mailgate issues list] makes it look like there are kind a few important outstanding issues (some with patches available, if you wish to tinker with that), so I decided not to use it and instead try to integrate [Mike Cardwell]'s script into Dovecot instead.

Dovecot has a very nice [Pigeonhole plugin], which provides [Sieve] scripts (and client-side management of them) to Dovecot. By integrating PGP encryption at this stage, not only do you not have to edit any Postfix configuration (which by itself is an exercise in patience), and this way every user on the system can now conditionally apply PGP encryption to incoming emails, specifying which encryption key to use for which emails.

The first step was to make Dovecot use the Pigeonhole plugin. This can be done by adding the sieve plugin to the [LDA] and/or [LMTP] protocols of Dovecot's configuration file:

	:::text
	protocol lda {
		mail_plugins = $mail_plugins sieve
	}
	protocol lmtp {
		mail_plugins = $mail_plugins sieve
	}

Now, we need to get Pigeonhole to use the [extprograms plugin], which allows Sieve scripts to call certain (whitelisted, of course) programs. Sadly, this plugin did not have a package on the [AUR][Arch User Repository] (a rare occurrence), so I [submitted my own][pigeonhole-extprograms package].

If you are not using [Arch][Arch Linux] or would rather not use this package, here is how you can build it:

Clone the repository:

	:::console
	$ hg clone http://hg.rename-it.nl/pigeonhole-0.3-sieve-extprograms
	$ cd pigeonhole*

Configure it (you may need to adjust the paths to match your installation; the paths below match the default Arch installation of Dovecot and Pigeonhole):

	:::console
	$ ./autogen.sh
	$ ./configure --prefix=/usr --with-dovecot=/usr/lib/dovecot --with-pigeonhole=/usr/include/dovecot/sieve --with-moduledir=/usr/lib/dovecot/modules

Build it:

	:::console
	$ make

Install it:

	:::console
	$ sudo make install

Now, Pigeonhole should have the extprograms plugin available. You need to enable it in Dovecot's configuration file:

	:::text
	plugin {
		sieve_plugins = sieve_extprograms
	}

However, the plugin by itself does nothing by default. You need to tell it what it can run, what is allowed, what is not, etc.

There are several ways to do this, as described on [the plugin page][extprograms plugin]. The way I went with it is to create a directory called `/etc/dovecot/sieve-filters`, and then creating symlinks inside that directory, pointing to the real programs that were to be run. This justifies its presence in `/etc`; it is not a directory full of scripts, but rather a directory indicating the set of scripts that are allowed to run.

Now you need to tell Pigeonhole about it, by adding to the `plugin` block described earlier:

	:::text
	plugin {
		sieve_plugins = sieve_extprograms
		sieve_extensions = +vnd.dovecot.filter
		sieve_filter_bin_dir = /etc/dovecot/sieve-filters
	}

Notice that `+vnd.dovecot.filter` was added to the `sieve_extensions` variable, *not `sieve_global_extensions`* as recommended on the extprograms plugin page. This is because we want to allow the user to customize the use of those filters.

Next, you need to grab [gpgit] and its dependencies:

	:::console
	$ cpan install MIME::Tools
	$ cpan install Mail::GnuPG
	$ git clone git://perot.me/gpgit # (Clone it in a safe place where you won't delete it accidentally)

And now we need to allow users to use it, by creating a symlink:

	:::console
	$ ln -s /path/to/gpgit/gpgit.pl /etc/dovecot/sieve-filters/gpgit

Now you can restart Dovecot and you should have the ability to use this in a Sieve script:

	:::text
	require ["fileinto", "vnd.dovecot.filter"];

	if address :matches "To" "me@domain.com" {
		filter "gpgit" "me@domain.com";
		fileinto "INBOX.encrypted";
		stop;
	}

This sample script would encrypt all emails sent to `me@domain.com` with `me@domain.com`'s PGP key, and file it into the "encrypted" IMAP folder.

But wait! This won't work yet. That is because Dovecot doesn't yet know what `me@domain.com`'s public key is.

Go back into your server and `su` into the user Pigeonhole is set to run Sieve filters as. Then import the keys into the keyring:

	:::console
	$ gpg --recv-keys (ID of me@domain.com PGP key here)

Now you need to mark it as trusted, otherwise `gpg` will refuse to encrypt data with it:

	:::console
	$ gpg --edit-key me@domain.com
	gpg> trust
	  1 = I don't know or won't say
	  2 = I do NOT trust
	  3 = I trust marginally
	  4 = I trust fully
	  5 = I trust ultimately
	  m = back to the main menu
	Your decision? 5
	Do you really want to set this key to ultimate trust? (y/N) y
	gpg> save

You're done! Wait for the next incoming email, and it should be encrypted with your PGP key.

You may also want to apply this to existing emails that you've already received; well, there's a [handy script for that too][encmaildir.sh].

Happy encrypting!

**EDIT**: Dovecot now has a built-in [mail-crypt-plugin] which provides at-rest [dcrypt] encryption of email data. The plugin performs both encryption and decryption of the emails on the server side, which means your email server still has to have access to the private keys in order for it to work. By contrast, the solution described in this blog post does not require the server to have access to your GnuPG private key. It can remain locally on your email client. It is possible to use both the plugin and this GnuPG solution together as well. Doing so is a good idea if you're not already doing full-disk-encryption on the filesystem used to store your email, as dcrypt encrypts email headers, while the GnuPG solution doesn't. Though you could achieve the same thing with other solutions, dcrypt makes it safer to back up your email data to a third-party backup facility in a way that doesn't reveal email metadata.

[My PGP key]: https://perot.me/pgp.asc
[Grepular - Automatically Encrypting all Incoming Email]: https://grepular.com/Automatically_Encrypting_all_Incoming_Email
[Exim]: http://www.exim.org/
[Postfix]: http://www.postfix.org/
[Dovecot]: http://dovecot.org/
[GPG-Mailgate]: https://code.google.com/p/gpg-mailgate/
[GPG-Mailgate issues list]: https://code.google.com/p/gpg-mailgate/issues/list
[Mike Cardwell]: https://grepular.com/
[Pigeonhole plugin]: http://wiki2.dovecot.org/Pigeonhole
[Sieve]: http://sieve.info/
[LDA]: http://wiki2.dovecot.org/LDA
[LMTP]: http://wiki2.dovecot.org/LMTP
[extprograms plugin]: http://wiki2.dovecot.org/Pigeonhole/Sieve/Plugins/Extprograms
[Arch User Repository]: https://aur.archlinux.org/
[pigeonhole-extprograms package]: https://aur.archlinux.org/packages/pigeonhole-extprograms-hg
[Arch Linux]: https://www.archlinux.org/
[gpgit]: https://github.com/EtiennePerot/gpgit
[encmaildir.sh]: https://github.com/EtiennePerot/gpgit/blob/master/encmaildir.sh
[mail-crypt-plugin]: https://doc.dovecot.org/configuration_manual/mail_crypt_plugin/
[dcrypt]: https://wiki.dovecot.org/Design/Dcrypt
