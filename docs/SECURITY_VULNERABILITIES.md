# Security Vulnerabilities

This document tracks known security vulnerabilities in dependencies and their current status.

## Current Vulnerabilities

### 1. ecdsa 0.19.1 - CVE-2024-23342 (Minerva Timing Attack)

**Status**: Known Issue - Out of Scope  
**Severity**: Medium  
**Affected**: Transitive dependency via python-jose  

**Description**:  
python-ecdsa has been found to be subject to a Minerva timing attack on the P-256 curve. Using the `ecdsa.SigningKey.sign_digest()` API function and timing signatures an attacker can leak the internal nonce which may allow for private key discovery.

**Impact**:  
- ECDSA signatures, key generation, and ECDH operations are affected
- ECDSA signature verification is unaffected
- This is a side-channel attack

**Official Response**:  
The python-ecdsa project considers side channel attacks out of scope for the project and there is no planned fix.

**Mitigation**:  
- This vulnerability is in a transitive dependency (python-jose → ecdsa)
- We don't directly use ecdsa in our codebase
- The vulnerability is considered out of scope by the upstream project
- No immediate action required

**References**:  
- [CVE-2024-23342](https://nvd.nist.gov/vuln/detail/CVE-2024-23342)
- [GHSA-wj6h-64fc-37mp](https://github.com/advisories/GHSA-wj6h-64fc-37mp)

### 2. requests 2.31.0 - Multiple CVEs

**Status**: Fixed in requirements.txt  
**Severity**: High  
**Affected**: Direct dependency  

**Vulnerabilities**:  
- CVE-2024-35195: Certificate verification bypass
- CVE-2024-47081: .netrc credentials leak

**Fix**:  
- Updated to requests==2.32.4 in requirements.txt
- This version includes fixes for both vulnerabilities

**References**:  
- [CVE-2024-35195](https://nvd.nist.gov/vuln/detail/CVE-2024-35195)
- [CVE-2024-47081](https://nvd.nist.gov/vuln/detail/CVE-2024-47081)

## Vulnerability Management Process

### 1. Regular Scanning
- Daily security scans via GitHub Actions
- Local scanning with `python scripts/test_security_workflow.py`
- Manual checks with `pip-audit` and `safety scan`

### 2. Assessment Criteria
- **Critical/High**: Immediate action required
- **Medium**: Evaluate impact and plan mitigation
- **Low**: Monitor and document

### 3. Response Actions
- Update dependencies when fixes are available
- Document known issues that cannot be immediately resolved
- Implement workarounds when possible
- Monitor for new fixes or alternative packages

### 4. Documentation
- All vulnerabilities are documented here
- Status updates are tracked
- Mitigation strategies are recorded

## Security Best Practices

1. **Keep Dependencies Updated**: Regular updates to latest secure versions
2. **Pin Versions**: Use exact version pins in requirements.txt
3. **Security Scanning**: Automated scanning in CI/CD pipeline
4. **Documentation**: Track all known vulnerabilities
5. **Risk Assessment**: Evaluate impact vs. effort for each vulnerability

## Reporting Security Issues

If you discover a security vulnerability in this project:

1. **DO NOT** create a public GitHub issue
2. Email security@sendapi.com (if available) or contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for assessment and response

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [Safety Documentation](https://pyup.io/safety/) 