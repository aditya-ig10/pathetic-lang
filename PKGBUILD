# PKGBUILD

# Maintainer: Your Name <your.email@example.com>
pkgname=pathetic
pkgver=0.1
pkgrel=1
pkgdesc="A lightweight meme-powered programming language for DSA practice"
arch=('x86_64')
url="https://github.com/yourusername/pathetic-lang"
license=('MIT')
depends=('python' 'python-setuptools')
makedepends=('git')
source=("git+https://github.com/yourusername/pathetic-lang.git#branch=main")
sha256sums=('SKIP')  # Using git source, so we skip checksum validation

package() {
    cd "$srcdir/pathetic-lang"

    # Install Python package using setuptools
    python setup.py install --root="$pkgdir"

    # Make the executable accessible system-wide
    install -Dm755 pathetic "$pkgdir/usr/bin/pathetic"
}
