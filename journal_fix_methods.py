    def _get_agent_instance(self, agent_name: str):
        """Get an agent instance by name"""
        if agent_name == "Zealot":
            return Zealot()
        elif agent_name == "Skeptic":
            return Skeptic()
        elif agent_name == "Trickster":
            return Trickster()
        else:
            raise ValueError(f"Unknown agent name: {agent_name}")

    async def _write_agent_journals(self):
        """Have each agent write a private journal entry"""
        logger.info(f"📔 Agents writing journal entries at cycle {self.cycle_count}")
        
        try:
            # Create journal logger
            journal_logger = DebateLogger(self.log_dir, self.cycle_count)
            journal_logger.log_event("=== AGENT JOURNAL ENTRIES ===", "System")
            
            # Have each agent write their journal
            for agent_name in self.agent_names:
                logger.info(f"📝 {agent_name} writing journal entry...")
                
                try:
                    # Get agent instance
                    agent = self._get_agent_instance(agent_name)
                    
                    # Write journal entry
                    journal_entry = await agent.write_journal_entry(
                        self.cycle_count, 
                        self.claude_client,
                        self.shared_memory
                    )
                    
                    journal_logger.log_event(f"JOURNAL by {agent_name}:", "Journal")
                    journal_logger.log_event(journal_entry, "Journal")
                    logger.info(f"✅ {agent_name} completed journal entry")
                    
                except Exception as e:
                    logger.error(f"❌ {agent_name} failed to write journal: {e}")
                    journal_logger.log_event(f"ERROR: {agent_name} journal failed: {str(e)}", "System")
            
            journal_logger.log_event("=== JOURNAL ENTRIES COMPLETED ===", "System")
            logger.info(f"✅ Journal entries completed for cycle {self.cycle_count}")
            
        except Exception as e:
            logger.error(f"❌ Error during journal writing: {e}")
            self.general_logger.log_event(f"ERROR during journal writing: {str(e)}", "System")