🔒 MFE Build Extra Certs - Tutor Plugin
######################################

*Corporate VPN certificates? No problem! 🏢*

Ever tried building Open edX MFE (Micro Frontend) applications in a corporate environment behind a VPN, only to watch your build fail with certificate / SSL errors? This plugin has got your back!

**What it does:** Seamlessly injects your corporate VPN certificates into MFE Docker builds, ensuring smooth deployments in enterprise environments.

🚀 **Features**
***************

- 🏗️ **Automatic Certificate Injection** - Patches the MFE Dockerfile to automatically detect and install VPN certificates
- 📁 **Simple CLI Management** - Easy commands to add, remove, and check certificate status
- 🔧 **Zero Configuration** - Works out of the box once you add your certificate
- 🌐 **Node.js Compatible** - Configures ``NODE_EXTRA_CA_CERTS`` for Node.js applications
- 🛡️ **Enterprise Ready** - Perfect for corporate environments with custom CA certificates

📦 **Installation**
*******************

.. code-block:: bash

    # Install the plugin
    pip install git+https://github.com/WGU-Open-edX/tutor-mfe-build-extra-certs.git

    # Enable it in Tutor
    tutor plugins enable mfe-build-extra-certs

🎯 **Quick Start**
******************

1. **Add your certificate:**

.. code-block:: bash

    tutor mfe-build-extra-certs set-cert /path/to/your/corporate-cert.crt

2. **Check it's working:**

.. code-block:: bash

    tutor mfe-build-extra-certs status

3. **Build your MFE with VPN support:**

.. code-block:: bash

    tutor images build mfe

That's it! Your MFE will now build successfully with your corporate VPN certificate trusted. ✨

🔧 **CLI Commands**
*******************

- ``status`` - Check if a certificate is configured
- ``set-cert <path>`` - Add a certificate for MFE builds
- ``remove-cert`` - Remove the current certificate

**Example:**

.. code-block:: bash

    # Check current status
    tutor mfe-build-extra-certs status

    # Add your company's certificate
    tutor mfe-build-extra-certs set-cert ~/Downloads/company-vpn-cert.crt

    # Remove certificate when no longer needed
    tutor mfe-extra-certs remove-cert

🔍 **How It Works**
*******************

This plugin patches the MFE Dockerfile to:

1. **Copy** any ``vpn-cert.*`` files into the container during build
2. **Install** the certificate into the system's CA certificate store
3. **Configure** Node.js to trust the certificate via ``NODE_EXTRA_CA_CERTS``
4. **Continue** gracefully if no certificate is present (won't break existing setups)

The certificate gets installed at ``/usr/local/share/ca-certificates/vpn-cert.crt`` and becomes trusted by both system tools and Node.js applications.

🏢 **Perfect For**
******************

- Corporate environments with custom CA certificates
- VPN-protected development environments
- Organizations with internal certificate authorities
- Any setup where HTTPS requests need custom certificate trust

🛠️ **Troubleshooting**
**********************

**Build still failing?**

- Ensure your certificate is in PEM format (``-----BEGIN CERTIFICATE-----``)
- Check the certificate path with ``tutor mfe-extra-certs status``
- Verify the certificate is valid and not expired

**Certificate not being picked up?**

- Make sure you enabled the plugin: ``tutor plugins enable mfe-vpn-extra-certs``
- Rebuild the MFE image after adding the certificate: ``tutor images build mfe``

** And remember this only helps with the Node build process, other SSL / Cert related issues may need some other configs outside of the scope of this plugin. **

📄 **License**
**************

This software is licensed under the terms of the AGPLv3.
