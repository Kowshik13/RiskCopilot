# Model Risk Management Policy
Version: 2.1
Last Updated: January 2024
Classification: Internal

## 1. Purpose and Scope

This Model Risk Management (MRM) policy establishes the framework for identifying, measuring, monitoring, and controlling risks arising from the use of quantitative models throughout Société Générale.

### 1.1 Scope
This policy applies to all models used for:
- Credit risk assessment
- Market risk measurement
- Operational risk quantification
- Regulatory capital calculation
- Pricing and valuation
- Stress testing and scenario analysis
- Anti-money laundering (AML) and fraud detection

## 2. Model Risk Definition

Model risk is the potential for adverse consequences from decisions based on incorrect or misused model outputs and reports. Model risk can lead to financial loss, poor business decisions, or damage to the bank's reputation.

### 2.1 Sources of Model Risk
- Fundamental errors in model methodology
- Incorrect implementation
- Use of models outside their intended purpose
- Data quality issues
- Model performance degradation over time

## 3. Model Governance Framework

### 3.1 Three Lines of Defense

**First Line: Model Owners and Users**
- Responsible for model development and implementation
- Ensure appropriate model use
- Monitor model performance
- Maintain model documentation

**Second Line: Model Risk Management Team**
- Independent model validation
- Model risk assessment and rating
- Policy development and maintenance
- Model inventory management

**Third Line: Internal Audit**
- Independent review of MRM framework
- Assessment of policy compliance
- Evaluation of control effectiveness

### 3.2 Model Lifecycle Management

**Phase 1: Development**
- Business case and requirements definition
- Methodology selection and justification
- Initial testing and documentation
- Peer review

**Phase 2: Validation**
- Independent validation by MRM team
- Conceptual soundness review
- Outcomes analysis
- Implementation verification
- Approval or rejection decision

**Phase 3: Implementation**
- Production deployment
- User access controls
- Change management procedures
- Initial monitoring setup

**Phase 4: Ongoing Monitoring**
- Performance tracking against thresholds
- Quarterly validation reports
- Annual model review
- Backtesting requirements

**Phase 5: Model Retirement**
- Decommissioning procedures
- Data retention requirements
- Documentation archival

## 4. Model Validation Requirements

### 4.1 Initial Validation
All models must undergo independent validation before production use, including:
- Evaluation of conceptual soundness
- Review of mathematical framework
- Data quality assessment
- Benchmarking against alternatives
- Sensitivity analysis
- Stress testing

### 4.2 Periodic Revalidation
- High-risk models: Annual validation
- Medium-risk models: Every 2 years
- Low-risk models: Every 3 years
- Triggered revalidation for material changes

### 4.3 Validation Documentation
Validation reports must include:
- Executive summary with key findings
- Detailed technical analysis
- Identified limitations and conditions of use
- Risk rating and recommendations
- Management responses and action plans

## 5. Model Risk Rating

Models are classified into risk tiers based on:
- Materiality of potential impact
- Model complexity
- Quality of input data
- Degree of model uncertainty

### 5.1 Risk Tiers
- **Tier 1 (Critical)**: Direct impact on regulatory capital, >€500M exposure
- **Tier 2 (High)**: Significant financial or strategic decisions, €100-500M exposure
- **Tier 3 (Medium)**: Moderate business impact, €10-100M exposure
- **Tier 4 (Low)**: Limited impact, <€10M exposure

## 6. Data Governance

### 6.1 Data Quality Standards
- Completeness: >95% for critical fields
- Accuracy: Regular reconciliation with source systems
- Timeliness: Data refresh within defined SLAs
- Consistency: Cross-system validation

### 6.2 Data Lineage
- Document data sources and transformations
- Maintain data dictionary
- Track data quality metrics
- Implement data quality controls

## 7. Model Performance Monitoring

### 7.1 Key Performance Indicators
- Prediction accuracy metrics (RMSE, MAE, etc.)
- Discrimination measures (Gini, KS statistic)
- Calibration tests
- Stability indices

### 7.2 Performance Thresholds
- Green: Performance within expected range
- Amber: Performance degradation requiring investigation
- Red: Material breach requiring immediate action

### 7.3 Backtesting Requirements
- Monthly backtesting for market risk models
- Quarterly backtesting for credit risk models
- Document and explain threshold breaches
- Escalation procedures for persistent breaches

## 8. Model Documentation Standards

### 8.1 Required Documentation
- Model development document
- Technical specification
- User guide
- Validation report
- Monitoring procedures
- Change log

### 8.2 Documentation Maintenance
- Update within 30 days of material changes
- Annual review for accuracy
- Version control requirements
- Retention period: 7 years minimum

## 9. Regulatory Compliance

### 9.1 Regulatory Requirements
Ensure compliance with:
- Basel III/IV requirements
- ECB TRIM guidelines
- SR 11-7 (Federal Reserve guidance)
- Local regulatory requirements

### 9.2 Regulatory Reporting
- Quarterly model inventory updates
- Annual MRM effectiveness assessment
- Ad-hoc regulatory submissions
- Audit findings and remediation status

## 10. Technology and Infrastructure

### 10.1 Model Development Environment
- Segregated development/test/production environments
- Version control for code and data
- Access controls and audit trails
- Approved software and tools list

### 10.2 Production Environment
- Change control procedures
- Automated monitoring and alerting
- Disaster recovery procedures
- Performance optimization

## 11. Roles and Responsibilities

### 11.1 Model Owner
- Ensure model fitness for purpose
- Monitor performance
- Maintain documentation
- Implement validation recommendations

### 11.2 Model User
- Use model within approved scope
- Report performance issues
- Understand model limitations
- Follow prescribed procedures

### 11.3 Model Risk Management
- Independent validation
- Policy maintenance
- Risk assessment
- Training and guidance

### 11.4 Senior Management
- Approve high-risk models
- Review MRM effectiveness
- Ensure adequate resources
- Foster risk culture

## 12. Training and Awareness

### 12.1 Training Requirements
- MRM fundamentals for all model users
- Technical training for developers
- Validation training for MRM team
- Annual refresher training

### 12.2 Competency Assessment
- Role-based competency requirements
- Regular skills assessment
- Training effectiveness measurement
- Continuous improvement

## 13. Exceptions and Waivers

### 13.1 Exception Process
- Document business justification
- Risk assessment and mitigation
- Approval by appropriate authority
- Time-bound with review dates

### 13.2 Approval Authority
- Tier 1 models: Board Risk Committee
- Tier 2 models: Chief Risk Officer
- Tier 3 models: Head of Model Risk
- Tier 4 models: Model Risk Manager

## 14. Policy Review and Updates

This policy is reviewed annually and updated as needed to reflect:
- Regulatory changes
- Industry best practices
- Lessons learned
- Organizational changes

## Appendices

### Appendix A: Model Inventory Template
### Appendix B: Validation Report Template
### Appendix C: Performance Monitoring Dashboard
### Appendix D: Regulatory Mapping
### Appendix E: Glossary of Terms

---
Document Control:
- Owner: Chief Risk Officer
- Approved by: Board Risk Committee
- Next Review: January 2025
- Distribution: All Model Stakeholders
