import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv, dotenv_values
 
class ProjectSetup:
    """Initialize and configure the AutoGen environment"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.env_file = self.project_root / ".env"
        
    def create_directories(self):
        """Create all necessary project directories"""
        print("📁 Creating project directories...")
        
        directories = [
            self.data_dir,
            self.data_dir / "documents",
            self.data_dir / "csv_files",
            self.data_dir / "faiss_index",
            self.data_dir / "chromadb",
            self.logs_dir,
            self.project_root / "agents",
            self.project_root / "utils",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created {directory}")
    
    def create_env_file(self):
        """Create .env file from template"""
        print("\n⚙️  Setting up environment configuration...")
        
        if not self.env_file.exists():
            template_file = self.project_root / ".env.template"
            if template_file.exists():
                with open(template_file, 'r') as f:
                    template_content = f.read()
                with open(self.env_file, 'w') as f:
                    f.write(template_content)
                print(f"  ✓ Created {self.env_file}")
                print("  ⚠️  Please update .env with your actual configuration")
            else:
                print("  ✗ .env.template not found")
        else:
            print(f"  ✓ {self.env_file} already exists")
    
    def validate_dependencies(self):
        """Validate that all required packages are installed"""
        print("\n📦 Validating dependencies...")
        
        required_packages = [
            ('pyautogen', 'pyautogen'),  # (import_name, display_name)
            ('langchain', 'langchain'),
            ('faiss', 'faiss'),
            ('chromadb', 'chromadb'),
            ('sqlalchemy', 'sqlalchemy'),
            ('redis', 'redis'),
            ('fastapi', 'fastapi'),
        ]
        
        missing_packages = []
        for import_name, display_name in required_packages:
            try:
                __import__(import_name)
                print(f"  ✓ {display_name}")
            except ImportError:
                missing_packages.append(display_name)
                print(f"  ✗ {display_name} (not installed)")
        
        if missing_packages:
            print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            print("Run: pip install -r requirements.txt")
            return False
        return True
    
    def create_config_file(self):
        """Create configuration JSON file"""
        print("\n🔧 Creating configuration file...")
        
        config = {
            "project": {
                "name": "Enterprise Knowledge Base with AutoGen",
                "version": "1.0.0",
                "environment": "development"
            },
            "autogen": {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 300
            },
            "agents": {
                "retriever": {
                    "type": "retriever",
                    "role": "Document and Database Retriever",
                    "description": "Retrieves relevant data from documents and databases"
                },
                "analyst": {
                    "type": "analyst",
                    "role": "Query Analyst",
                    "description": "Interprets queries and analyzes retrieved data"
                },
                "fact_checker": {
                    "type": "fact_checker",
                    "role": "Fact Checker",
                    "description": "Validates answers against source documents"
                },
                "synthesizer": {
                    "type": "synthesizer",
                    "role": "Answer Synthesizer",
                    "description": "Generates final polished answers"
                }
            },
            "retrieval": {
                "sql_enabled": True,
                "rag_enabled": True,
                "hybrid_mode": True
            },
            "storage": {
                "vector_db": "faiss",
                "cache_db": "redis",
                "session_db": "sqlite"
            }
        }
        
        config_path = self.project_root / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"  ✓ Created {config_path}")
        return config
    
    def setup(self):
        """Run complete setup"""
        print("=" * 60)
        print("🚀 ENTERPRISE KB WITH AUTOGEN - PROJECT SETUP")
        print("=" * 60)
        
        self.create_directories()
        self.create_env_file()
        self.create_config_file()
        
        if self.validate_dependencies():
            print("\n" + "=" * 60)
            print("✅ PROJECT SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Update .env file with your configuration")
            print("2. Add sample documents to data/documents/")
            print("3. Add CSV files to data/csv_files/")
            print("4. Run: python main.py")
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ Setup incomplete. Install missing dependencies.")
            print("=" * 60)
            return False
 
if __name__ == "__main__":
    load_dotenv()
    setup = ProjectSetup()
    success = setup.setup()
    sys.exit(0 if success else 1)
 
