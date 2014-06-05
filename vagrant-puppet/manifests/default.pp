exec { 'apt-get update':
  path => '/usr/bin',
}

package { 'python-pip':         ensure => 'installed' }
package { 'python-numpy':       ensure => 'installed' }
package { 'python-dev':         ensure => 'installed' }
package { 'python-networkx':    ensure => 'installed' }
package { 'python-nose':        ensure => 'installed' }

# For some of the minc-widgets tools:
package { 'libgetopt-tabular-perl': ensure => 'installed' }
package { 'imagemagick':            ensure => 'installed' }

$handy_packages = [ 'ipython', 'htop', 'screen' ]
package { $handy_packages: ensure => 'installed' }

$minc_packages = [ 'git', 'cmake', 'cmake-curses-gui', 'build-essential', 'g++', 'bison', 'flex', 'freeglut3', 'freeglut3-dev', 'libxi6', 'libxi-dev', 'libxmu6', 'libxmu-dev', 'libxmu-headers' ]
package { $minc_packages: ensure => 'installed' }

vcsrepo { '/opt/code/minc-toolkit':
  ensure => present,
  provider => git,
  source => 'https://github.com/BIC-MNI/minc-toolkit.git',
  revision => 'master',
  require => Package[$minc_packages],
}

exec { 'compile minc-tools':
    timeout => 17280, # 24 hours! Just for testing...

    require => Vcsrepo['/opt/code/minc-toolkit'],

    command => '/vagrant/build_minc_tools.sh',

    # FIXME Should get the full list of these...
    creates => ['/usr/local/bin/minc_anlm', '/usr/local/bin/mincaverage', '/usr/local/bin/mincbbox', '/usr/local/bin/mincbeast', '/usr/local/bin/mincblob', '/usr/local/bin/mincblur', '/usr/local/bin/minccalc', '/usr/local/bin/mincchamfer', '/usr/local/bin/mincconcat', '/usr/local/bin/mincconvert', '/usr/local/bin/minccopy', '/usr/local/bin/mincdefrag', '/usr/local/bin/mincdiff', '/usr/local/bin/minc_downsample', '/usr/local/bin/mincdump', '/usr/local/bin/mincedit', '/usr/local/bin/mincexpand', '/usr/local/bin/mincextract', '/usr/local/bin/mincgen', '/usr/local/bin/mincheader', '/usr/local/bin/minchistory', '/usr/local/bin/mincinfo', '/usr/local/bin/minclookup', '/usr/local/bin/mincmakescalar', '/usr/local/bin/mincmakevector', '/usr/local/bin/mincmask', '/usr/local/bin/mincmath', '/usr/local/bin/minc_modify_header', '/usr/local/bin/mincmorph', '/usr/local/bin/mincnlm', '/usr/local/bin/minc_nuyl', '/usr/local/bin/mincpik', '/usr/local/bin/minc_pretty_pic_m.pl', '/usr/local/bin/minc_pretty_pic.pl', '/usr/local/bin/minc_qc2.pl', '/usr/local/bin/minc_qc.pl', '/usr/local/bin/minc_qc_rgb.pl', '/usr/local/bin/minc_qc_t2t1.pl', '/usr/local/bin/minc_rank', '/usr/local/bin/mincresample', '/usr/local/bin/mincreshape', '/usr/local/bin/mincsample', '/usr/local/bin/mincskel', '/usr/local/bin/mincstats', '/usr/local/bin/minctoecat', '/usr/local/bin/minctoraw', '/usr/local/bin/minc_to_rgb', '/usr/local/bin/minctotag', '/usr/local/bin/minctracc', '/usr/local/bin/mincview', '/usr/local/bin/mincwindow']
}

vcsrepo { '/opt/code/pyminc':
  ensure   => present,
  provider => git,
  source   => 'https://github.com/mcvaneede/pyminc.git',
  revision => 'master',
  require  => Exec['compile minc-tools'],
}

exec { 'install pyminc':
    require     => Vcsrepo['/opt/code/pyminc'],
    command     => '/usr/bin/python setup.py install',
    cwd         => '/opt/code/pyminc',
}

exec { 'install nibabel':
    require => Package['python-pip', 'python-numpy', 'python-dev'],
    command => '/usr/bin/pip install nibabel',
}

exec { 'install traits':
    require => Package['python-pip', 'python-dev'],
    command => '/usr/bin/pip install traits traitsui',
}

vcsrepo { '/opt/code/nipype':
    ensure => present,
    provider => git,
    source => 'https://github.com/nipy/nipype.git',
    revision => 'master',
    require  => [Exec['install nibabel'], Exec['install traits'], Package['python-networkx'], Package['python-dev'], Package['python-nose']]
}

exec { 'install nipype':
    require     => Vcsrepo['/opt/code/nipype'],
    command     => '/usr/bin/python setup.py install',
    cwd         => '/opt/code/nipype',
}

vcsrepo { '/opt/code/minc-widgets':
  ensure   => present,
  provider => git,
  source   => 'https://github.com/BIC-MNI/minc-widgets.git',
  revision => 'master',
  require  => Exec['compile minc-tools'],
}

exec { 'tweak PATH for minc-widgets':
    require     => Vcsrepo['/opt/code/minc-widgets'],
    command     => "/bin/echo 'export PATH=$PATH:/opt/code/minc-widgets/gennlxfm:/opt/code/minc-widgets/mincbigaverage:/opt/code/minc-widgets/mincnorm:/opt/code/minc-widgets/nlpfit:/opt/code/minc-widgets/volalign:/opt/code/minc-widgets/volcentre:/opt/code/minc-widgets/volextents:/opt/code/minc-widgets/volflip:/opt/code/minc-widgets/voliso:/opt/code/minc-widgets/volpad:/opt/code/minc-widgets/volsymm:/opt/code/minc-widgets/xfmavg:/opt/code/minc-widgets/xfmflip' >> /etc/bash.bashrc",
}

# volgenmodel-nipype
vcsrepo { '/opt/code/volgenmodel-nipype':
    ensure => present,
    provider => git,
    source => 'https://github.com/carlohamalainen/volgenmodel-nipype.git',
    revision => 'master',
    require  => Exec['install nipype']
}

exec { 'tweak PYTHONPATH and PATH for volgenmodel-nipype':
    require     => Vcsrepo['/opt/code/volgenmodel-nipype'],
    command     => "/bin/echo 'export PYTHONPATH=/opt/code/volgenmodel-nipype' >> /etc/bash.bashrc; /bin/echo 'export PATH=$PATH:/opt/code/volgenmodel-nipype/extra-scripts' >> /etc/bash.bashrc",
    cwd         => '/opt/code/nipype',
}
