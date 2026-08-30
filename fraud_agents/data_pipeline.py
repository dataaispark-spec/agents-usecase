"""
Data Ingestion Pipeline for Multi-Agent Fraud Detection System
Supports: PaySim, IEEE-CIS, BAF, Credit Card Fraud datasets
Maps to specialized agents: Device/Network, User Behavior, KYC, Adjudication
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Generator
from datetime import datetime, timedelta
import json
from pathlib import Path
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetType(Enum):
    """Supported fraud detection datasets"""
    PAYSIM = "paysim"  # Mobile Money & P2P Transfers
    IEEE_CIS = "ieee_cis"  # Card-Not-Present e-Commerce
    BAF = "baf"  # Bank Account Fraud (KYC)
    CREDIT_CARD_ULB = "credit_card_ulb"  # Credit Card Anomaly
    FINANCIAL_REPORTS = "financial_reports"  # Corporate Fraud
    STREAM_SIMULATOR = "stream_simulator"  # Real-time streaming


class AgentTarget(Enum):
    """Target agent for each data type"""
    DEVICE_NETWORK = "device_network_agent"
    USER_BEHAVIOR = "user_behavior_agent"
    KYC_IDENTITY = "kyc_identity_agent"
    LEDGER_AUDIT = "ledger_audit_agent"
    ADJUDICATION = "adjudication_agent"
    COMPLIANCE = "compliance_agent"


class DataIngestionPipeline:
    """
    Enterprise-grade data ingestion pipeline for BFSI fraud detection.
    Routes dataset features to specialized multi-agent system components.
    """
    
    def __init__(self, dataset_type: DatasetType, config: Optional[Dict] = None):
        self.dataset_type = dataset_type
        self.config = config or {}
        self.batch_size = self.config.get('batch_size', 1000)
        self.streaming = self.config.get('streaming', False)
        
        # Feature mappings for each dataset type
        self.feature_mappings = self._get_feature_mappings()
        
        logger.info(f"Initialized pipeline for {dataset_type.value}")
    
    def _get_feature_mappings(self) -> Dict[DatasetType, Dict]:
        """Define feature mappings from datasets to agent inputs"""
        return {
            DatasetType.PAYSIM: {
                'target_agent': AgentTarget.LEDGER_AUDIT,
                'features': [
                    'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg',
                    'newbalanceOrig', 'nameDest', 'oldbalanceDest',
                    'newbalanceDest', 'isFraud', 'isFlaggedFraud'
                ],
                'derived_features': [
                    'balance_change_orig', 'balance_change_dest',
                    'transaction_velocity', 'round_trip_flag'
                ],
                'agent_routing': {
                    'amount': [AgentTarget.USER_BEHAVIOR, AgentTarget.ADJUDICATION],
                    'type': [AgentTarget.LEDGER_AUDIT],
                    'nameOrig': [AgentTarget.USER_BEHAVIOR, AgentTarget.KYC_IDENTITY],
                    'nameDest': [AgentTarget.LEDGER_AUDIT, AgentTarget.DEVICE_NETWORK]
                }
            },
            DatasetType.IEEE_CIS: {
                'target_agent': AgentTarget.DEVICE_NETWORK,
                'features': [
                    'TransactionID', 'TransactionDT', 'TransactionAmt',
                    'ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5',
                    'card6', 'addr1', 'addr2', 'dist1', 'dist2',
                    'P_emaildomain', 'R_emaildomain', 'C1', 'C2', 'C3',
                    'D1', 'D2', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6',
                    'V1', 'V2', 'V3', 'id_01', 'id_02', 'id_03',
                    'id_04', 'id_05', 'id_06', 'id_07', 'id_08',
                    'id_09', 'id_10', 'id_11', 'id_12', 'id_13',
                    'id_14', 'id_15', 'id_16', 'id_17', 'id_18',
                    'id_19', 'id_20', 'id_21', 'id_22', 'id_23',
                    'id_24', 'id_25', 'id_26', 'id_27', 'id_28',
                    'id_29', 'id_30', 'id_31', 'id_32', 'id_33',
                    'id_34', 'id_35', 'id_36', 'id_37', 'id_38'
                ],
                'derived_features': [
                    'device_fingerprint', 'ip_proxy_score', 'geo_velocity',
                    'email_domain_risk', 'card_bin_risk'
                ],
                'agent_routing': {
                    'TransactionAmt': [AgentTarget.USER_BEHAVIOR, AgentTarget.ADJUDICATION],
                    'id_31': [AgentTarget.DEVICE_NETWORK],  # Device type
                    'id_33': [AgentTarget.DEVICE_NETWORK],  # Device dimensions
                    'P_emaildomain': [AgentTarget.DEVICE_NETWORK, AgentTarget.KYC_IDENTITY]
                }
            },
            DatasetType.BAF: {
                'target_agent': AgentTarget.KYC_IDENTITY,
                'features': [
                    'applicant_id', 'application_date', 'employment_status',
                    'income', 'credit_score', 'debt_to_income', 'age',
                    'gender', 'education', 'marital_status', 'address_zip',
                    'phone_number', 'email_domain', 'previous_applications',
                    'fraud_label'
                ],
                'derived_features': [
                    'synthetic_identity_score', 'income_consistency',
                    'address_velocity', 'application_frequency'
                ],
                'agent_routing': {
                    'credit_score': [AgentTarget.KYC_IDENTITY, AgentTarget.ADJUDICATION],
                    'income': [AgentTarget.KYC_IDENTITY],
                    'application_date': [AgentTarget.USER_BEHAVIOR]
                }
            },
            DatasetType.CREDIT_CARD_ULB: {
                'target_agent': AgentTarget.USER_BEHAVIOR,
                'features': ['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7',
                          'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15',
                          'V16', 'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23',
                          'V24', 'V25', 'V26', 'V27', 'V28', 'Amount', 'Class'],
                'derived_features': [
                    'transaction_frequency', 'amount_deviation',
                    'time_since_last_transaction', 'spending_pattern_anomaly'
                ],
                'agent_routing': {
                    'Amount': [AgentTarget.USER_BEHAVIOR, AgentTarget.ADJUDICATION],
                    'Time': [AgentTarget.USER_BEHAVIOR],
                    'V1-V28': [AgentTarget.DEVICE_NETWORK, AgentTarget.USER_BEHAVIOR]
                }
            }
        }
    
    def load_paysim_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load PaySim synthetic financial dataset
        Models mobile money transactions with multi-step transfer schemes
        """
        logger.info(f"Loading PaySim dataset from {file_path}")
        df = pd.read_csv(file_path)
        
        # Validate expected columns
        expected_cols = ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg',
                        'newbalanceOrig', 'nameDest', 'oldbalanceDest',
                        'newbalanceDest', 'isFraud', 'isFlaggedFraud']
        
        missing_cols = set(expected_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Add derived features
        df = self._add_paysim_derived_features(df)
        
        logger.info(f"Loaded {len(df):,} PaySim transactions")
        logger.info(f"Fraud rate: {df['isFraud'].mean():.4f}")
        
        return df
    
    def _add_paysim_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for PaySim dataset"""
        # Balance changes
        df['balance_change_orig'] = df['oldbalanceOrg'] - df['newbalanceOrig']
        df['balance_change_dest'] = df['newbalanceDest'] - df['oldbalanceDest']
        
        # Round-trip flag (money returns to originator)
        df['round_trip_flag'] = (df['nameOrig'] == df['nameDest']).astype(int)
        
        # Transaction velocity per account (rolling window)
        df = df.sort_values(['nameOrig', 'step'])
        df['transaction_velocity'] = df.groupby('nameOrig').cumcount() + 1
        
        return df
    
    def load_ieee_cis_dataset(self, train_path: str, test_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load IEEE-CIS Fraud Detection dataset
        Complex multi-table relational data with device fingerprints
        """
        logger.info(f"Loading IEEE-CIS dataset from {train_path}")
        train_df = pd.read_csv(train_path)
        
        if test_path:
            test_df = pd.read_csv(test_path)
            test_df['isFraud'] = -1  # Unknown labels in test set
            df = pd.concat([train_df, test_df], ignore_index=True)
        else:
            df = train_df
        
        # Add derived features
        df = self._add_ieee_cis_derived_features(df)
        
        logger.info(f"Loaded {len(df):,} IEEE-CIS transactions")
        if 'isFraud' in df.columns:
            fraud_rate = df[df['isFraud'] != -1]['isFraud'].mean()
            logger.info(f"Fraud rate: {fraud_rate:.4f}")
        
        return df
    
    def _add_ieee_cis_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for IEEE-CIS dataset"""
        # Device fingerprint hash
        device_cols = [col for col in df.columns if col.startswith('id_')]
        if device_cols:
            df['device_fingerprint'] = df[device_cols].apply(
                lambda x: hash(tuple(x.fillna('NA'))), axis=1
            )
        
        # Email domain risk scoring
        if 'P_emaildomain' in df.columns:
            high_risk_domains = ['tempmail.com', 'guerrillamail.com', '10minutemail.com']
            df['email_domain_risk'] = df['P_emaildomain'].apply(
                lambda x: 1 if any(domain in str(x).lower() for domain in high_risk_domains) else 0
            )
        
        return df
    
    def load_baf_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load Bank Account Fraud (BAF) dataset from NeurIPS 2022
        Focuses on account opening fraud and synthetic identities
        """
        logger.info(f"Loading BAF dataset from {file_path}")
        df = pd.read_csv(file_path)
        
        # Add derived features
        df = self._add_baf_derived_features(df)
        
        logger.info(f"Loaded {len(df):,} BAF applications")
        if 'fraud_label' in df.columns:
            logger.info(f"Fraud rate: {df['fraud_label'].mean():.4f}")
        
        return df
    
    def _add_baf_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for BAF dataset"""
        # Synthetic identity score (simplified heuristic)
        if all(col in df.columns for col in ['age', 'income', 'credit_score']):
            df['synthetic_identity_score'] = (
                (df['age'] < 25).astype(int) * 0.3 +
                (df['income'] > 100000).astype(int) * 0.2 +
                (df['credit_score'] > 750).astype(int) * 0.2
            )
        
        # Application frequency
        if 'applicant_id' in df.columns and 'application_date' in df.columns:
            df['application_date'] = pd.to_datetime(df['application_date'])
            df = df.sort_values(['applicant_id', 'application_date'])
            df['application_frequency'] = df.groupby('applicant_id').cumcount() + 1
        
        return df
    
    def load_credit_card_ulb_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load Credit Card Fraud Detection dataset (ULB Machine Learning Group)
        Industry-standard anonymized PCA-transformed vectors
        """
        logger.info(f"Loading Credit Card ULB dataset from {file_path}")
        df = pd.read_csv(file_path)
        
        # Add derived features
        df = self._add_credit_card_derived_features(df)
        
        logger.info(f"Loaded {len(df):,} credit card transactions")
        if 'Class' in df.columns:
            logger.info(f"Fraud rate: {df['Class'].mean():.6f}")
        
        return df
    
    def _add_credit_card_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for Credit Card dataset"""
        # Time-based features
        df['hour'] = (df['Time'] // 3600) % 24
        df['day_of_week'] = (df['Time'] // (3600 * 24)) % 7
        
        # Amount statistics
        df['amount_log'] = np.log1p(df['Amount'])
        
        # Rolling statistics (if sorted by time)
        df = df.sort_values('Time')
        df['rolling_mean_amount'] = df['Amount'].rolling(window=10, min_periods=1).mean()
        df['rolling_std_amount'] = df['Amount'].rolling(window=10, min_periods=1).std()
        df['amount_deviation'] = (df['Amount'] - df['rolling_mean_amount']) / (df['rolling_std_amount'] + 1e-6)
        
        return df
    
    def generate_streaming_data(self, dataset_type: DatasetType, 
                               duration_minutes: int = 60,
                               transactions_per_minute: int = 100) -> Generator[Dict, None, None]:
        """
        Generate real-time streaming data for testing multi-agent system
        Simulates Kafka-like event stream
        """
        logger.info(f"Generating {duration_minutes}min stream at {transactions_per_minute} txn/min")
        
        start_time = datetime.now()
        transaction_id = 1000000
        
        for minute in range(duration_minutes):
            current_minute = start_time + timedelta(minutes=minute)
            
            for _ in range(transactions_per_minute):
                transaction = self._generate_synthetic_transaction(
                    dataset_type, transaction_id, current_minute
                )
                transaction_id += 1
                
                yield transaction
            
            # Simulate time passing
            # In production, this would be real-time streaming
    
    def _generate_synthetic_transaction(self, dataset_type: DatasetType,
                                       transaction_id: int,
                                       timestamp: datetime) -> Dict:
        """Generate a single synthetic transaction based on dataset type"""
        
        if dataset_type == DatasetType.PAYSIM:
            transaction_types = ['TRANSFER', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'CASH_IN']
            is_fraud = np.random.choice([0, 1], p=[0.99, 0.01])
            amount = np.random.exponential(1000) if not is_fraud else np.random.exponential(5000)
            
            return {
                'TransactionID': f"PAYSIM_{transaction_id}",
                'Timestamp': timestamp.isoformat(),
                'step': int((timestamp - datetime.now()).total_seconds() // 3600),
                'type': np.random.choice(transaction_types),
                'amount': round(amount, 2),
                'nameOrig': f"C{np.random.randint(100000, 999999)}",
                'oldbalanceOrg': round(np.random.uniform(1000, 50000), 2),
                'newbalanceOrig': round(np.random.uniform(500, 45000), 2),
                'nameDest': f"M{np.random.randint(10000, 99999)}",
                'oldbalanceDest': round(np.random.uniform(0, 30000), 2),
                'newbalanceDest': round(np.random.uniform(0, 35000), 2),
                'isFraud': is_fraud,
                'isFlaggedFraud': 1 if amount > 10000 and is_fraud else 0,
                'metadata': {
                    'source_dataset': 'paysim',
                    'target_agents': ['ledger_audit', 'user_behavior']
                }
            }
        
        elif dataset_type == DatasetType.IEEE_CIS:
            is_fraud = np.random.choice([0, 1], p=[0.96, 0.04])
            
            return {
                'TransactionID': f"IEEE_{transaction_id}",
                'Timestamp': timestamp.isoformat(),
                'TransactionDT': int((timestamp - datetime(2017, 12, 1)).total_seconds()),
                'TransactionAmt': round(np.random.exponential(100), 2),
                'ProductCD': np.random.choice(['W', 'H', 'C', 'S', 'R']),
                'card1': np.random.randint(10000, 99999),
                'card4': np.random.choice(['visa', 'mastercard', 'amex', 'discover']),
                'card6': np.random.choice(['debit', 'credit']),
                'P_emaildomain': np.random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'tempmail.com']),
                'id_31': np.random.choice(['chrome', 'firefox', 'safari', 'edge']),
                'id_33': f"{np.random.randint(300, 2000)}x{np.random.randint(200, 1500)}",
                'DeviceType': np.random.choice(['desktop', 'mobile', 'tablet']),
                'DeviceInfo': f"Windows {np.random.randint(7, 11)}.0",
                'isFraud': is_fraud,
                'metadata': {
                    'source_dataset': 'ieee_cis',
                    'target_agents': ['device_network', 'adjudication']
                }
            }
        
        # Default fallback
        return {
            'TransactionID': f"GEN_{transaction_id}",
            'Timestamp': timestamp.isoformat(),
            'Amount': round(np.random.exponential(100), 2),
            'isFraud': np.random.choice([0, 1], p=[0.98, 0.02]),
            'metadata': {
                'source_dataset': 'synthetic',
                'target_agents': ['user_behavior']
            }
        }
    
    def route_to_agents(self, transaction: Dict) -> Dict[AgentTarget, Dict]:
        """
        Route transaction features to appropriate specialized agents
        Implements the multi-agent message queue pattern
        """
        routing_result = {}
        feature_map = self.feature_mappings.get(self.dataset_type, {})
        agent_routing = feature_map.get('agent_routing', {})
        
        for field, value in transaction.items():
            if field in agent_routing:
                target_agents = agent_routing[field]
                for agent in target_agents:
                    if agent not in routing_result:
                        routing_result[agent] = {'features': {}}
                    routing_result[agent]['features'][field] = value
        
        # Add metadata to each agent payload
        for agent in routing_result:
            routing_result[agent]['metadata'] = {
                'transaction_id': transaction.get('TransactionID'),
                'timestamp': transaction.get('Timestamp'),
                'routing_timestamp': datetime.now().isoformat()
            }
        
        return routing_result
    
    def process_batch(self, transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Process a batch of transactions and route to agents
        Returns agent-specific payloads
        """
        agent_payloads = {agent.value: [] for agent in AgentTarget}
        
        for txn in transactions:
            routed = self.route_to_agents(txn)
            for agent_target, payload in routed.items():
                agent_payloads[agent_target.value].append(payload)
        
        # Filter out empty lists
        agent_payloads = {k: v for k, v in agent_payloads.items() if v}
        
        return agent_payloads
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive data quality validation for fraud detection datasets
        """
        validation_report = {
            'total_records': len(df),
            'missing_values': {},
            'duplicate_records': 0,
            'outliers_detected': {},
            'data_drift_indicators': {},
            'quality_score': 100.0
        }
        
        # Missing values
        for col in df.columns:
            missing_pct = df[col].isna().mean() * 100
            if missing_pct > 0:
                validation_report['missing_values'][col] = round(missing_pct, 2)
        
        # Duplicates
        validation_report['duplicate_records'] = df.duplicated().sum()
        
        # Outlier detection (simple IQR method for numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
            if outliers > 0:
                validation_report['outliers_detected'][col] = int(outliers)
        
        # Calculate quality score
        missing_penalty = sum(validation_report['missing_values'].values()) / len(df.columns)
        duplicate_penalty = (validation_report['duplicate_records'] / len(df)) * 100
        validation_report['quality_score'] = max(0, 100 - missing_penalty - duplicate_penalty)
        
        return validation_report


def demo_pipeline():
    """Demonstrate the data ingestion pipeline with synthetic data"""
    
    print("=" * 80)
    print("CLERIVON AI - MULTI-AGENT FRAUD DETECTION DATA PIPELINE DEMO")
    print("=" * 80)
    
    # Initialize pipeline for PaySim dataset
    pipeline = DataIngestionPipeline(DatasetType.PAYSIM, {'batch_size': 100})
    
    print("\n📊 DATASET: PaySim Mobile Money Transactions")
    print("-" * 80)
    
    # Generate streaming data
    print("\n🔄 Generating real-time transaction stream...")
    stream_generator = pipeline.generate_streaming_data(
        DatasetType.PAYSIM,
        duration_minutes=5,
        transactions_per_minute=50
    )
    
    # Process first 10 transactions
    transactions_processed = 0
    fraud_detected = 0
    
    for transaction in stream_generator:
        transactions_processed += 1
        if transaction['isFraud'] == 1:
            fraud_detected += 1
        
        # Route to agents
        routed = pipeline.route_to_agents(transaction)
        
        if transactions_processed <= 3:
            print(f"\n✓ Transaction #{transaction['TransactionID']}")
            print(f"  Amount: ${transaction['amount']:.2f}")
            print(f"  Type: {transaction['type']}")
            print(f"  Fraud Flag: {'⚠️ FRAUD' if transaction['isFraud'] else '✅ Normal'}")
            agent_names = [agent.value for agent in routed.keys()]
            print(f"  Routed to Agents: {', '.join(agent_names)}")
        
        if transactions_processed >= 10:
            break
    
    print(f"\n📈 STREAM SUMMARY:")
    print(f"  Total Transactions: {transactions_processed}")
    print(f"  Fraud Detected: {fraud_detected} ({fraud_detected/transactions_processed*100:.1f}%)")
    print(f"  Agents Engaged: {len(AgentTarget)}")
    
    # Demonstrate batch processing
    print("\n\n📦 BATCH PROCESSING DEMO")
    print("-" * 80)
    
    batch_transactions = list(pipeline.generate_streaming_data(
        DatasetType.PAYSIM,
        duration_minutes=1,
        transactions_per_minute=20
    ))
    
    agent_payloads = pipeline.process_batch(batch_transactions)
    
    print(f"\nProcessed batch of {len(batch_transactions)} transactions")
    print(f"Distributed to {len(agent_payloads)} agent queues:")
    
    for agent_name, payloads in agent_payloads.items():
        print(f"  • {agent_name}: {len(payloads)} payloads")
    
    # Data quality validation
    print("\n\n🔍 DATA QUALITY VALIDATION")
    print("-" * 80)
    
    # Create sample DataFrame - flatten metadata for pandas compatibility
    flat_transactions = []
    for txn in batch_transactions:
        flat_txn = {k: v for k, v in txn.items() if not isinstance(v, dict)}
        flat_txn['metadata_source'] = txn.get('metadata', {}).get('source_dataset')
        flat_transactions.append(flat_txn)
    
    sample_df = pd.DataFrame(flat_transactions)
    validation = pipeline.validate_data_quality(sample_df)
    
    print(f"\nQuality Score: {validation['quality_score']:.1f}/100")
    print(f"Total Records: {validation['total_records']}")
    print(f"Duplicate Records: {validation['duplicate_records']}")
    
    if validation['missing_values']:
        print(f"Missing Values: {len(validation['missing_values'])} columns")
    
    if validation['outliers_detected']:
        print(f"Outliers Detected: {len(validation['outliers_detected'])} columns")
    
    print("\n" + "=" * 80)
    print("✅ PIPELINE DEMO COMPLETE")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Connect to Kafka/RabbitMQ for production streaming")
    print("2. Configure agent-specific feature extraction")
    print("3. Deploy to Kubernetes with auto-scaling")
    print("4. Monitor data drift with continuous validation")


if __name__ == "__main__":
    demo_pipeline()
