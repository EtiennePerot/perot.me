Title:          Is Ubuntu still a Linux distribution*?
Author:         Etienne Perot <etienne (at) perot (dot) me>
Date:           2013-03-07
License:        CC-BY-3.0
ThumbnailUrl:   ubuntu-eclipse.png
CanonicalImage: silos.png

With the recent [announcement][Mir release announcement] that Ubuntu would be switching to Canonical's new [Mir display server][Mir specification document], Ubuntu is increasingly distancing itself from other Linux distributions on various levels. In order to approach the subject, we first need to define what a Linux distribution really is.

Most people agree that [Android] is not a Linux distribution. Sure, it may run the Linux kernel, but that is only secondary to the overall Android system. Most of its applications run in a Java virtual machine, and the system does a lot of things differently than most Linux distributions do (e.g. its graphics stack, input management, power management, software management, etc.). Most of these subsystems have drifted far apart from most Linux distributions, as a result of Android being targeted at mobile devices (low-power, touch-centric, etc). There is nothing inherently wrong with this approach, but it means that said subsystems cannot easily be incorporated back into regular Linux distributions, for various reasons. Some systems may not make sense in a non-Android environment (e.g. the Google Play Store), some of them make assumptions that a general-purpose distribution cannot ("there will be a touch screen"), some of them depend on other Android-specific code, etc. However, those systems can be used (and are being used) in *Android distributions* such as [CyanogenMod] or [ParanoidAndroid].

Therefore, divergence of core software *creates a new ecosystem*, rather than *contributing to the one it originated from*. This distinction is important in order to give credence to the following definition of "Linux distribution":

> *A Linux distribution is an operating system along with a set of software contributions which benefit the overall Linux software ecosystem.

By this definition, does Ubuntu still qualify as a Linux distribution? Let's find out.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Display server

[![Mir image][]][Mir specification document]

This one is probably the easiest point to make. Canonical has [announced][Mir release announcement] that they will use [Mir][Mir specification document], a new display server that has been developed in-house [since June 2012][Mir development: first code commit]. The [Mir specification document] states that this move was required because the trusty old [X display server] is broken in countlessly many ways (which is true; Watch [this talk][The Real Story Behind Wayland and X] if you are not convinced of this), because Weston (the reference [Wayland] compositor) doesn't fulfill all of their requirements (which is [highly][Aaron Seigo: "I really don't feel like pointing out the obvious (to me, anyways) technical limitations in their current designs."]&nbsp;[debatable][UI customization on Wayland]), and because Android's [SurfaceFlinger] doesn't fulfill all of their requirements either. Thus, rather than [researching the subject][Canonical developer removes FUD about Wayland] or contributing to the Wayland project, they decided to implement their own solution: Mir.

As a result, Ubuntu will be the only operating system to use the Mir display server. Given [its poor reception][Upstream X/Wayland Developers Bash Canonical, Mir], it is not likely that other distributions will eagerly adopt Mir any time soon. Things may change, but as it stands, Ubuntu (and possibly its derivatives) will be the only operating system using Mir for the foreseeable future. Mir will be a cause of fragmentation for the Linux graphics landscape, rather than a contribution to it.

## Graphics drivers

[![Jockey image thumbnail][]][Jockey dialog]

As a direct consequence of changing the display server to Mir, Ubuntu now requires its own set of proprietary graphics drivers. The current crop of proprietary graphics drivers only target X and cannot be used for Mir at this time; they would either need to be extended to support Mir or new drivers should be created altogether. Canonical claims it is currently [speaking with Nvidia][Mir: An outpost envisioned as a new home] and [other vendors][Canonical confirms talks with other GPU vendors] in order to address this issue.

Therefore, if Ubuntu is the only operating system to use Mir, then it will also be the only operating system to use these new graphics drivers. Those drivers would be useless on distributions that are not using Mir. What's more concerning is that this moves attention and developer time away from writing drivers for Wayland or improving the existing ones for X. Splitting developer time means less-polished drivers for everyone. This is a lose-lose situation.

## Init daemon

[![Upstart image][]][Upstart]

It has been the case for [quite some time now][Beta Release of Ubuntu 6.10] that Ubuntu uses [Upstart] as init daemon. Currently, Google's [Chromium OS] is [the only other Linux distribution using Upstart][Upstart Adoption], so while Ubuntu is not the only operating system to use it, most other distributions have either updated to [systemd] or are still using [SysVInit]. It remains to be seen as to whether Chromium OS will switch to systemd as well; it [started using Upstart][Chromium OS commit: Changes to upstartify more of our init scripts] months prior to the [announcement of systemd]. It was the best choice at the time to get the boot performance they were aiming for. Now, this may [not be the case anymore][systemd speed]. A lot of distributions, some of which used Upstart in the past, have moved on to systemd or will switch to it in their next release ([Fedora][systemd in Fedora], [Mandriva][systemd in Mandriva] and [derivatives][systemd in Mageia], [Red Hat Entreprise Linux][systemd in Red Hat Entreprise Linux], [Arch Linux][systemd in Arch Linux] and [derivatives][systemd in Chakra Linux], [openSUSE][systemd in openSUSE]).

## Desktop shell

[![Unity image][]][Unity]

Canonical has been hard at work on its in-house shell interface, [Unity]. It was rough around the edges at first, and has since then [grown][Ars Technica: Ubuntu 12.04 and the Unity HUD reviewed]&nbsp;[into a][Engadget: Ubuntu 12.04 review]&nbsp;[usable][Lunduke.com: Ubuntu 12.04 Review]&nbsp;[state][The Register - Ubuntu 12.04 hits beta, brings smooth Unity for marching masses]. However, perhaps because Canonical tends to [use it as a vehicle for controversial decisions][perot.me: Ubuntu privacy blunder over Amazon ads continues] or perhaps simply because [it was not easy to package in its early days][Fedora and openSUSE Linux Drop Unity Efforts], adoption on other Linux distributions hasn't caught on despite [being][Unity on Arch Linux]&nbsp;[possible][Unity on Fedora]. Unfortunately, there are no usage statistics or non-anecdotal evidence to back up this assessment, but perhaps the fact that Ubuntu's most popular non-DE-oriented derivative, [Linux Mint], [decided not to use Unity][Linux Mint: No to Unity, no to Gnome-Shell] and went as far as [rolling their own instead][Cinnamon], may indicate a lack of confidence from the community.

## Software management

[![Ubuntu Software Center image][]][Ubuntu Apps Directory]

As Ubuntu is a Debian-based operating system, it inherits Debian's package management system through .deb packages and Apt repositories. So far, so good; this is very standard.

And then there's the [Ubuntu Software Center]. It is primarily a frontend to the Apt package management system, but it also includes the ability to offer [commercial software][Ubuntu Software Center: Commercial software FAQs]. However, the Ubuntu Software Center isn't simply selling *software*; it is selling *packages containing binaries made specifically for a single version of Ubuntu*. Using those packages on Ubuntu versions other than the one it was purchased on, or on non-Ubuntu Linux distributions, [is not supported][Ubuntu Payment FAQ: Can I use Software Center purchases on other distros or other OSes?]. Similar to the way buying software on Apple's App Store doesn't give you access to the same software on non-Apple platforms, buying software on Ubuntu's Software Center doesn't give you access to the same software on non-Ubuntu platforms. This is different from other means of software delivery such as [Steam] or [Desura] which give you access to all available versions of the software, or even buying it directly from the author's website. This decision locks the user into the Ubuntu platform if they don't want to pay again to get the same software on a different platform.

## Approach to software development

[![Shuttleworth Steve Jobs][]][Ubuntu for phones keynote]

One's approach to software development hugely impacts whether or not the software created by said approach helps or hinders the ecosystem.

Of course, since Ubuntu is an operating system running the Linux kernel and various other [GPL]-licensed software, their contributions to said projects ([which][AppArmor]&nbsp;[do][Upstart]&nbsp;[exist][Uncomplicated Firewall][!][Offspring Image Build System]) are licensed under the GPL as well, facilitating their adoption in other Linux distributions. Everything about this is good.

But then there's Canonical's latest projects such as Unity, [Ubuntu for phones] and [for tablets][Ubuntu for tablets], and Mir. Those are examples of what [Mark Shuttleworth refers to as "skunkworks"][Mark Shuttleworth: Raring community skunkworks]:

> Items with high "tada!" value that would be great candidates for folk who want to work on something that will get attention when unveiled.

Indeed, all of these projects have followed the same release pattern: Let it stew internally for a few months and, once it's at boiling point (i.e. when it's almost usable but too far in development for anyone to reasonably object to further development), unleash it to the public in a sudden manner. Effectively, this means that the project is secret, closed source, and out of the reach of public scrutiny and criticism for months on end. Then, once the figurative point of no return is reached, the project is unveiled, creating the aforementioned "high 'tada!' value". This marketing strategy may be effective at getting the attention from media outlets and the like, but it's just that: a marketing strategy. The problem with it is that it goes against the idea of a collaborative development approach, in which multiple developers from multiple backgrounds with different interests keep each other in check as development progresses. Without continuous exposure to critics, a sudden reveal means all of the (pent-up) criticism is suddenly unleashed all at once, hence the backslash over Mir. Not only that, it causes a huge amount of duplicated effort and additional fragmentation. Had Canonical expressed interest in working on a display server upfront, rather than only [starting to hint at it more than half a year after development on it had started][OMG! Ubuntu!: Is Canonical Working on New, Custom Display Server for Unity?], the Wayland developers would have probably pointed them in the right direction, helped them with their experience with the Linux graphics stack (something which [the current Mir developers seem not to have in spades][Phoronix: The Developers Behind The Mir Display Server]), and hopefully keep development relatively close to the existing Wayland protocol (or conversely, adapted Wayland to follow Canonical's effort closely) such that no fragmentation would have been needed at all, or perhaps such that only one of the two projects would need to exist at all.

In [a blog post about Mir][Mir: An outpost envisioned as a new home], one of Canonical's Mir developers said:

> In the case of Weston, the lack of a clearly defined driver model as well as the **lack of a rigorous development process in terms of testing** driven by a set of well-defined requirements gave us doubts whether it would help us to reach the “moon”. *[emphasis added]*

Read this a few times. What is it trying to say? It is saying that Weston was not a valid candidate because it didn't fit into Canonical's [test-driven development] model. There may be some truth to that, but is that enough of a reason to completely ignore an existing, promising, open solution, rather than simply add unit tests to it? It may be a lot of tedious work, but in the long run it would still be less work than the resulting cost of developing and maintaining a completely separate piece of software from scratch and fragmenting the ecosystem in the process.

He goes on to say:

> We looked further and found Google’s SurfaceFlinger, a standalone compositor that fulfilled some but not all of our requirements. It benefits from its consistent driver model that is widely adopted and supported within the industry and it fulfills a clear set of requirements. It's rock-solid and stable, but **we did not think that it would empower us to fulfill our mission** of a tightly integrated user experience that scales across form-factors. *[emphasis added]*

The only criticism of SurfaceFlinger is that "it wouldn't empower [them] to fulfill [their] mission". What mission? "A tightly integrated user experience that scales across form-factors.". It's no secret that Android runs just fine on many screen sizes from [tiny][Android on a 3-inch phone] to [small][Android on a 4-inch phone] to [medium][Android on a 13-inch tablet] to [huge][Android on TVs], so the "scales across form-factors" certainly isn't the cause here. We are left with:

> We did not think that it would empower us to fulfill our mission of a tightly integrated user experience.

Canonical rejected SurfaceFlinger because it didn't empower them. Why? Because they **couldn't control it enough** to create that "tightly integrated user experience" they are after. They rejected SurfaceFlinger because it wasn't under their control. This speaks volumes.

## Community communication

[![Ubuntu installfest][]][Ubuntu LoCo]

It's no secret that Canonical has been struggling with communication recently. Canonical's top representatves have had trouble getting their points across, such as the ["Erm, we have root"][Mark Shuttleworth: Amazon search results in the Dash] post by Mark Shuttleworth, along with [his ambiguous statements on "secret projects"][Mark Shuttleworth: Raring community skunkworks] which required [having to post a follow-up article to clarify the matter][Mark Shuttleworth: "in addition to" follow-up]. And then there's [calling Stallman "childish"][Jono Bacon: On Richard Stallman and Ubuntu], thankfully followed by [an apology regarding this statement][Jono Bacon: On Being Childish; An Apology]. There is definitely a message delivery problem here. Not only that, there's also been some [disregard towards popular community requests by triaging them away][Launchpad bug: Don't include remote searches in the home lens][.][HelpLinux: Remove unsafe packages from Ubuntu LiveCD]

And then there's the [departure of prominent Ubuntu members from the community][Martin Owens not renewing his Ubuntu membership]. Some of the [comments][Alex Murray leaving Ubuntu as a user and a developer]&nbsp;[on][Andrea Grandi hesitating about leaving the Ubuntu community]&nbsp;[that][Ubuntu Studio Developer Scott Lavender doesn't feel part of the community anymore]&nbsp;[article][Sarah Hobbs deactivating her Ubuntu membership]&nbsp;[are][Sam Spilsbury (former Canonical employee) agreeing that there is no Ubuntu community anymore]&nbsp;[quite][Jeff Spaleta: Canonical is being more honest]&nbsp;[interesting][Canonical developer Michael Hall acknowledging the situation]. Other members are feeling like their work is [being][Pasi Lallinaho: Is UDS no longer UDS?]&nbsp;[left][Elizabeth Krumbach: On the Ubuntu Community]&nbsp;[out][Andrea Grandi: UDS happening online only]. It is clear that [something is definitely wrong with the Ubuntu community][Compiz developer's take on the Ubuntu/Canonical community].

The recent outrage over Mir is only part of the problem, but it is a significant part of it. Not only does it [make developers feel "pissed on"][Wayland developer: "Don't Piss On Wayland"], it also [puts an additional burden on them to cool off the resulting FUD][KWin developer on Mir].

To be clear, such community discontent *doesn't change* whether or not Ubuntu should be considered a Linux distribution or not; however, Ubuntu's popularity and the size of its following are directly correlated with how far its new technologies will spread to the rest of the ecosystem. Low popularity breeds isolation.

## Conclusion

As Ubuntu has grown, Canonical has tended to diverge from the rest of the Linux ecosystem and following its own path rather than trying to work with existing solutions, alienating part of its community in the process. This isn't news to anyone; [people have been quick to notice][Ubuntu Brainstorm: Cannot read the word "Linux" anywhere] that the word "Linux" hasn't been seen anywhere near the [Ubuntu.com] home page for quite a while now.

There is nothing wrong with differentiation. Differentiation is how distributions stand out from the crowd and how innovation happens: by doing its own thing and by doing it better than anyone else. However, differentiation isn't the same thing as [siloing oneself away][Information silo]. Differentiation doesn't have to imply rupturing one's ties to their roots; siloing does.

Now may be a good time to reassess whether or not Ubuntu's divergence has arrived at a point where it is no longer appropriate to consider Ubuntu as part of the **Linux** software ecosystem, but rather as part of the **Ubuntu** software ecosystem.

[![Ubuntu silo image thumbnail][]][Ubuntu silo image]

**Update**: [Jono Bacon responds to community concerns]. Mark Shuttleworth also posted [some][Mark Shuttleworth: Not convinced by rolling releases (includes some community matters)]&nbsp;[blog][Mark Shuttleworth: Misplaced criticism]&nbsp;[posts][Mark Shuttleworth: All the faces of Ubuntu] in response to criticism. It is good to see them responding to the community's concerns.

<span class="footnote">
**Image acknowledgements**:
	[Starry Night](http://www.publicdomainpictures.net/view-image.php?image=23995&picture=starry-night&large=1),
	various official Linux distributions' logos,
	[Ubuntu devices photo](http://www.ubuntu.com/devices),
	[Jockey screenshot from Ubuntu Vibes](http://www.ubuntuvibes.com/2011/10/nvidia-and-ati-post-release-driver.html),
	[Upstart Logo](https://bazaar.launchpad.net/~upstart-devel/upstart/trunk/view/head:/doc/upstart-logo.svg),
	[Mark Shuttleworth photo by crshbndct](http://www.reddit.com/user/crshbndct),
	[Ubuntu installfest 2011](http://nlsthzn.com/2012/10/31/rainbow-nation/),
	[Apple Inc. logo](https://en.wikipedia.org/wiki/File:Apple_Computer_Logo_rainbow.svg),
	[Silo image](https://en.wikipedia.org/wiki/File:Silo_-_height_extension_by_adding_hoops_and_staves.jpg).
</span>

[Mir release announcement]: https://lists.ubuntu.com/archives/ubuntu-devel/2013-March/036776.html
[Mir specification document]: https://wiki.ubuntu.com/MirSpec
[Android]: http://www.android.com/
[CyanogenMod]: http://www.cyanogenmod.org/
[ParanoidAndroid]: http://www.paranoid-rom.com/
[Mir image]: mir-devices.png
[Mir development: first code commit]: https://bazaar.launchpad.net/~mir-team/mir/trunk/revision/2
[X display server]: https://en.wikipedia.org/wiki/X_Window_System
[The Real Story Behind Wayland and X]: https://www.youtube.com/watch?v=RIctzAQOe44
[Canonical developer removes FUD about Wayland]: http://www.phoronix.com/scan.php?page=news_item&px=MTMxODY
[Aaron Seigo: "I really don't feel like pointing out the obvious (to me, anyways) technical limitations in their current designs."]: https://plus.google.com/107555540696571114069/posts/hzRy1rJaafc
[UI customization on Wayland]: https://vignatti.wordpress.com/2013/03/05/ui-customization-on-wayland/
[Upstream X/Wayland Developers Bash Canonical, Mir]: http://www.phoronix.com/scan.php?page=news_item&px=MTMxNzY
[Jockey image thumbnail]: jockey-thumbnail.png
[Jockey dialog]: jockey.png
[Canonical confirms talks with other GPU vendors]: https://twitter.com/omgubuntu/status/309391113909854209
[Wayland]: http://wayland.freedesktop.org/
[SurfaceFlinger]: http://people.debian.org.tw/~olv/surfaceflinger/surfaceflinger.pdf
[Mir: An outpost envisioned as a new home]: https://samohtv.wordpress.com/2013/03/04/mir-an-outpost-envisioned-as-a-new-home/
[Mir specification: Mir on hardware supported by closed source drivers]: https://wiki.ubuntu.com/MirSpec#Mir_on_HW_Supported_By_Closed_Source_Drivers
[Upstart image]: upstart.png
[Beta Release of Ubuntu 6.10]: https://lists.ubuntu.com/archives/ubuntu-announce/2006-September/000090.html
[Upstart]: http://upstart.ubuntu.com/
[Chromium OS]: http://dev.chromium.org/chromium-os
[Upstart Adoption]: https://en.wikipedia.org/wiki/Upstart#Adoption
[systemd]: http://freedesktop.org/wiki/Software/systemd/
[SysVInit]: https://en.wikipedia.org/wiki/Init#SysV-style
[Chromium OS commit: Changes to upstartify more of our init scripts]: https://git.chromium.org/gitweb/?p=chromiumos/platform/init.git;a=commit;h=270de7e55d32c4e3a6fbdd43698ef9d6c00ccd63
[announcement of systemd]: http://0pointer.de/blog/projects/systemd.html
[systemd speed]: https://plus.google.com/108087225644395745666/posts/LyPQgKdntgA
[systemd in Fedora]: https://fedoraproject.org/wiki/Fedora_15_announcement
[systemd in Mandriva]: http://wiki.mandriva.com/en/2011.0_Notes#Systemd
[systemd in Mageia]: https://wiki.mageia.org/en/Mageia_2_Release_Notes#Systemd_.2F_Initscripts
[systemd in Red Hat Entreprise Linux]: https://www.youtube.com/watch?v=yhQIVXrCd68&t=37m10s
[systemd in Arch Linux]: https://www.archlinux.org/news/systemd-is-now-the-default-on-new-installations/
[systemd in Chakra Linux]: http://chakra-linux.org/news/index.php?/archives/77-Full-switch-to-Systemd-with-Claire-2012.10-ISO-released-today.html/
[systemd in openSUSE]: https://en.opensuse.org/Product_highlights#Infrastructure
[Unity image]: unity-dash.png
[Unity]: https://unity.ubuntu.com/
[Ars Technica: Ubuntu 12.04 and the Unity HUD reviewed]: http://arstechnica.com/information-technology/2012/05/precision-and-purpose-ubuntu-12-04-and-the-unity-hud-reviewed/
[Engadget: Ubuntu 12.04 review]: http://www.engadget.com/2012/05/01/ubuntu-12-04-precise-pangolin-review/
[Lunduke.com: Ubuntu 12.04 Review]: http://lunduke.com/?p=2813
[The Register - Ubuntu 12.04 hits beta, brings smooth Unity for marching masses]: http://www.theregister.co.uk/2012/03/02/ubuntu_12_04_beta_review/
[perot.me: Ubuntu privacy blunder over Amazon ads continues]: https://perot.me/ubuntu-privacy-blunder-over-amazon-ads-continues
[Fedora and openSUSE Linux Drop Unity Efforts]: https://www.pcworld.com/article/220085/fedora_and_opensuse_linux_drop_unity_efforts.html
[Unity on Arch Linux]: https://wiki.archlinux.org/index.php/Unity
[Unity on Fedora]: http://www.omgubuntu.co.uk/2012/07/unity-desktop-available-for-fedora
[Linux Mint]: http://www.linuxmint.com/
[Linux Mint: No to Unity, no to Gnome-Shell]: http://www.omgubuntu.co.uk/2010/11/linux-mint-no-to-unity-no-to-gnome-shell
[Cinnamon]: https://en.wikipedia.org/wiki/Cinnamon_%28user_interface%29
[Ubuntu Software Center]: https://wiki.ubuntu.com/SoftwareCenter
[Ubuntu Software Center image]: softwarecenter.png
[Ubuntu Apps Directory]: https://apps.ubuntu.com/
[Ubuntu Software Center: Commercial software FAQs]: https://developer.ubuntu.com/publish/commercial-software-faqs/
[Ubuntu Payment FAQ: Can I use Software Center purchases on other distros or other OSes?]: https://help.ubuntu.com/community/Pay/FAQs/USC_OtherOSes
[Steam]: https://store.steampowered.com/
[Desura]: http://www.desura.com/games
[Shuttleworth Steve Jobs]: mark-shuttlejobs.png
[Ubuntu for phones keynote]: https://www.youtube.com/watch?v=cpWHJDLsqTU
[GPL]: https://en.wikipedia.org/wiki/GNU_General_Public_License
[AppArmor]: http://apparmor.net/
[Offspring Image Build System]: https://launchpad.net/offspring
[Uncomplicated Firewall]: https://launchpad.net/ufw
[Ubuntu for phones]: http://www.ubuntu.com/devices/phones
[Ubuntu for tablets]: http://www.ubuntu.com/devices/tablet
[Mark Shuttleworth: Raring community skunkworks]: http://www.markshuttleworth.com/archives/1200
[OMG! Ubuntu!: Is Canonical Working on New, Custom Display Server for Unity?]: http://www.omgubuntu.co.uk/2013/02/canonical-working-on-new-display-server
[Phoronix: The Developers Behind The Mir Display Server]: http://www.phoronix.com/scan.php?page=news_item&px=MTMxNzc
[test-driven development]: https://en.wikipedia.org/wiki/Test-driven_development
[Android on a 3-inch phone]: https://www.samsung.com/uk/consumer/mobile-devices/smartphones/android/GT-S6010BBABTU
[Android on a 4-inch phone]: https://www.google.com/nexus/4/
[Android on a 13-inch tablet]: http://www.engadget.com/2012/06/25/toshiba-excite-13-review/
[Android on TVs]: https://developers.google.com/tv/
[Ubuntu installfest]: ubuntu-installfest.png
[Ubuntu LoCo]: http://loco.ubuntu.com/
[Mark Shuttleworth: Amazon search results in the Dash]: http://www.markshuttleworth.com/archives/1182
[Launchpad bug: Don't include remote searches in the home lens]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1054776
[HelpLinux: Remove unsafe packages from Ubuntu LiveCD]: http://www.helplinux.ru/wiki/en:kb:make-ubuntu-safe
[Mark Shuttleworth: "in addition to" follow-up]: http://www.markshuttleworth.com/archives/1207
[Jono Bacon: On Richard Stallman and Ubuntu]: http://www.jonobacon.org/2012/12/07/on-richard-stallman-and-ubuntu/
[Jono Bacon: On Being Childish; An Apology]: http://www.jonobacon.org/2012/12/10/on-being-childish-an-apology/
[Martin Owens not renewing his Ubuntu membership]: http://doctormo.org/2013/03/06/ubuntu-membership-2/
[Alex Murray leaving Ubuntu as a user and a developer]: http://doctormo.org/2013/03/06/ubuntu-membership-2/comment-page-1/#comment-15844
[Andrea Grandi hesitating about leaving the Ubuntu community]: http://doctormo.org/2013/03/06/ubuntu-membership-2/comment-page-1/#comment-15847
[Ubuntu Studio Developer Scott Lavender doesn't feel part of the community anymore]: http://doctormo.org/2013/03/06/ubuntu-membership-2/comment-page-1/#comment-15850
[Sarah Hobbs deactivating her Ubuntu membership]: http://doctormo.org/2013/03/06/ubuntu-membership-2/comment-page-1/#comment-15851
[Sam Spilsbury (former Canonical employee) agreeing that there is no Ubuntu community anymore]: http://doctormo.org/2013/03/06/ubuntu-membership-2/comment-page-1/#comment-15854
[Jeff Spaleta: Canonical is being more honest]: http://doctormo.org/2013/03/06/ubuntu-membership-2/comment-page-1/#comment-15859
[Canonical developer Michael Hall acknowledging the situation]: http://doctormo.org/2013/03/06/ubuntu-membership-2/comment-page-1/#comment-15863
[Pasi Lallinaho: Is UDS no longer UDS?]: http://open.knome.fi/2013/03/04/is-uds-no-longer-uds/
[Elizabeth Krumbach: On the Ubuntu Community]: http://princessleia.com/journal/?p=7670
[Andrea Grandi: UDS happening online only]: http://www.andreagrandi.it/2013/03/05/uds-happening-online-only-pros-and-cons/
[Compiz developer's take on the Ubuntu/Canonical community]: https://smspillaz.wordpress.com/2013/03/06/delivering-free-software-to-the-masses/
[Wayland developer: "Don't Piss On Wayland"]: http://www.phoronix.com/scan.php?page=news_item&px=MTMxODA
[KWin developer on Mir]: http://blog.martin-graesslin.com/blog/2013/03/war-is-peace/
[Ubuntu silo image thumbnail]: silos-thumbnail.png
[Ubuntu silo image]: silos.png
[Ubuntu Brainstorm: Cannot read the word "Linux" anywhere]: http://brainstorm.ubuntu.com/idea/27182/
[Ubuntu.com]: http://www.ubuntu.com/
[Information silo]: https://en.wikipedia.org/wiki/Information_silo
[Jono Bacon responds to community concerns]: http://www.jonobacon.org/2013/03/08/thoughts-on-recent-community-concerns/
[Mark Shuttleworth: Not convinced by rolling releases (includes some community matters)]: http://www.markshuttleworth.com/archives/1228
[Mark Shuttleworth: Misplaced criticism]: http://www.markshuttleworth.com/archives/1232
[Mark Shuttleworth: All the faces of Ubuntu]: http://www.markshuttleworth.com/archives/1235
