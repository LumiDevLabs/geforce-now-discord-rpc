#!/usr/bin/env bash
# Run this ONCE on your Mac to create the persistent signing certificate.
# It prints two values to add as GitHub Actions repository secrets:
#
#   CODESIGN_CERT_P12_BASE64  – base64-encoded p12 bundle
#   CODESIGN_CERT_PASSWORD    – the password protecting it
#
# After adding the secrets, every GitHub Actions build will sign the app with
# the same identity, so macOS Screen Recording grants survive app updates.
#
# The p12 is also saved to ~/.gfn-discord-rpc-signing/identity.p12 so local
# builds work too (build.sh picks it up automatically).
set -euo pipefail

SIGN_DIR="$HOME/.gfn-discord-rpc-signing"
P12_PATH="$SIGN_DIR/identity.p12"
CERT_PASSWORD="gfn-discord-rpc"
IDENTITY_CN="GFN Discord RPC"

if [[ -f "$P12_PATH" ]]; then
    echo "Certificate already exists at $P12_PATH"
    echo "Delete it first if you want to regenerate (this will break existing grants)."
    echo ""
else
    mkdir -p "$SIGN_DIR"
    tmp="$(mktemp -d)"

    cat > "$tmp/openssl.cnf" <<EOF
[ req ]
distinguished_name = dn
x509_extensions = v3
prompt = no
[ dn ]
CN = $IDENTITY_CN
[ v3 ]
basicConstraints = critical,CA:false
keyUsage = critical,digitalSignature
extendedKeyUsage = critical,codeSigning
EOF

    openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
        -keyout "$tmp/key.pem" -out "$tmp/cert.pem" -config "$tmp/openssl.cnf" \
        2>/dev/null

    openssl pkcs12 -export \
        -inkey "$tmp/key.pem" -in "$tmp/cert.pem" \
        -name "$IDENTITY_CN" -out "$P12_PATH" \
        -passout "pass:$CERT_PASSWORD"

    rm -rf "$tmp"
    echo "Created: $P12_PATH"
    echo ""
fi

echo "========================================================"
echo "Add these two secrets to your GitHub repository:"
echo "  Settings → Secrets and variables → Actions → New repository secret"
echo "========================================================"
echo ""
echo "Secret name:  CODESIGN_CERT_P12_BASE64"
echo "Secret value:"
base64 -i "$P12_PATH"
echo ""
echo "Secret name:  CODESIGN_CERT_PASSWORD"
echo "Secret value: $CERT_PASSWORD"
echo ""
echo "========================================================"
echo "IMPORTANT: never delete $P12_PATH"
echo "Regenerating the cert will invalidate Screen Recording grants for all users."
echo "========================================================"
