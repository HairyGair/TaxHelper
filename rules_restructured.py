"""
Restructured Rules Screen with Modern Interface Design
Complete UI overhaul for transaction categorization rules
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func
from models import Rule, Transaction, MATCH_MODES, INCOME_TYPES, EXPENSE_CATEGORIES
from utils import format_currency
from components.ui.interactions import show_toast, confirm_delete

def render_restructured_rules_screen(session, settings):
    """
    Render a completely restructured rules management interface
    """
    
    # ============================================================================
    # HEADER SECTION
    # ============================================================================
    st.markdown("# ⚙️ Categorization Rules")
    st.markdown("**Automate transaction categorization with smart matching rules**")
    
    # ============================================================================
    # HOW IT WORKS
    # ============================================================================
    with st.expander("💡 **How Rules Work**", expanded=False):
        st.markdown("""
        Rules automatically categorize your transactions when importing bank statements:
        
        **Match Modes:**
        - **Contains**: Matches if the text appears anywhere in the description
        - **Starts with**: Matches if the description begins with the text
        - **Ends with**: Matches if the description ends with the text
        - **Equals**: Exact match (case-insensitive)
        - **Regex**: Advanced pattern matching for complex rules
        
        **Priority System:**
        - Lower priority numbers are applied first (1 = highest priority)
        - If multiple rules match, the highest priority (lowest number) wins
        - Recommended: Use 10, 20, 30... to leave room for additions
        
        **Example:**
        - Rule: "TESCO" → Expense: Groceries
        - Any transaction containing "TESCO" will be categorized as Groceries expense
        """)
    
    # ============================================================================
    # QUICK STATS
    # ============================================================================
    
    # Get rule statistics
    total_rules = session.query(func.count(Rule.id)).scalar() or 0
    active_rules = session.query(func.count(Rule.id)).filter(Rule.enabled == True).scalar() or 0
    income_rules = session.query(func.count(Rule.id)).filter(Rule.map_to == "Income").scalar() or 0
    expense_rules = session.query(func.count(Rule.id)).filter(Rule.map_to == "Expense").scalar() or 0
    ignore_rules = session.query(func.count(Rule.id)).filter(Rule.map_to == "Ignore").scalar() or 0
    
    # Calculate rules effectiveness (how many transactions were auto-categorized)
    auto_categorized = session.query(func.count(Transaction.id)).filter(
        Transaction.confidence_score > 0
    ).scalar() or 0
    
    total_transactions = session.query(func.count(Transaction.id)).scalar() or 0
    effectiveness = (auto_categorized / total_transactions * 100) if total_transactions > 0 else 0
    
    # Display stats
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            label="Total Rules",
            value=f"{total_rules}",
            delta=f"{active_rules} active",
            help="Total number of categorization rules"
        )
    
    with col2:
        st.metric(
            label="Income Rules",
            value=f"{income_rules}",
            help="Rules that categorize as income"
        )
    
    with col3:
        st.metric(
            label="Expense Rules",
            value=f"{expense_rules}",
            help="Rules that categorize as expenses"
        )
    
    with col4:
        st.metric(
            label="Ignore Rules",
            value=f"{ignore_rules}",
            help="Rules that mark as personal/ignore"
        )
    
    with col5:
        st.metric(
            label="Auto-Categorized",
            value=f"{auto_categorized:,}",
            help="Transactions categorized by rules"
        )
    
    with col6:
        st.metric(
            label="Effectiveness",
            value=f"{effectiveness:.1f}%",
            help="Percentage of transactions auto-categorized"
        )
    
    st.markdown("---")
    
    # ============================================================================
    # QUICK RULE BUILDER
    # ============================================================================
    with st.expander("🚀 **Quick Rule Builder** - Create rules from common patterns", expanded=True):
        st.markdown("#### Select a common pattern to create a rule:")
        
        col1, col2, col3, col4 = st.columns(4)
        
        quick_rules = {
            "🛒 Supermarkets": [
                ("TESCO", "Expense", "Groceries"),
                ("SAINSBURY", "Expense", "Groceries"),
                ("ASDA", "Expense", "Groceries"),
                ("MORRISONS", "Expense", "Groceries"),
                ("LIDL", "Expense", "Groceries"),
                ("ALDI", "Expense", "Groceries"),
                ("WAITROSE", "Expense", "Groceries"),
                ("M&S FOOD", "Expense", "Groceries")
            ],
            "⛽ Fuel & Transport": [
                ("SHELL", "Expense", "Motor expenses"),
                ("BP", "Expense", "Motor expenses"),
                ("ESSO", "Expense", "Motor expenses"),
                ("UBER", "Expense", "Travel"),
                ("TRAINLINE", "Expense", "Travel"),
                ("TFL.GOV.UK", "Expense", "Travel")
            ],
            "💼 Business Services": [
                ("AMAZON WEB", "Expense", "Computer costs"),
                ("GOOGLE", "Expense", "Advertising"),
                ("FACEBOOK", "Expense", "Advertising"),
                ("MICROSOFT", "Expense", "Computer costs"),
                ("ADOBE", "Expense", "Computer costs"),
                ("DROPBOX", "Expense", "Computer costs")
            ],
            "🏦 Banking & Transfers": [
                ("INTEREST", "Income", "Interest"),
                ("DIVIDEND", "Income", "Dividends"),
                ("TRANSFER FROM", "Ignore", ""),
                ("TRANSFER TO", "Ignore", ""),
                ("STANDING ORDER", "Ignore", ""),
                ("DIRECT DEBIT", "Ignore", "")
            ]
        }
        
        selected_category = None
        
        with col1:
            if st.button("🛒 Supermarkets", use_container_width=True):
                selected_category = "🛒 Supermarkets"
        with col2:
            if st.button("⛽ Fuel & Transport", use_container_width=True):
                selected_category = "⛽ Fuel & Transport"
        with col3:
            if st.button("💼 Business Services", use_container_width=True):
                selected_category = "💼 Business Services"
        with col4:
            if st.button("🏦 Banking", use_container_width=True):
                selected_category = "🏦 Banking & Transfers"
        
        if selected_category:
            st.session_state['quick_category'] = selected_category
        
        if 'quick_category' in st.session_state:
            selected_category = st.session_state['quick_category']
            st.info(f"Selected: **{selected_category}**")
            
            # Show rules for this category
            rules_to_add = quick_rules[selected_category]
            
            # Display as a table with checkboxes
            st.markdown("Select rules to add:")
            
            selected_rules = []
            for rule_text, map_to, category in rules_to_add:
                col1, col2, col3, col4 = st.columns([0.5, 2, 1, 1])
                with col1:
                    if st.checkbox("", key=f"quick_{rule_text}"):
                        selected_rules.append((rule_text, map_to, category))
                with col2:
                    st.write(f"**{rule_text}**")
                with col3:
                    st.write(f"→ {map_to}")
                with col4:
                    st.write(category if category else "N/A")
            
            if selected_rules:
                if st.button(f"➕ Add {len(selected_rules)} Selected Rules", type="primary"):
                    added_count = 0
                    for rule_text, map_to, category in selected_rules:
                        # Check if rule already exists
                        existing = session.query(Rule).filter(
                            Rule.text_to_match == rule_text
                        ).first()
                        
                        if not existing:
                            new_rule = Rule(
                                match_mode="Contains",
                                text_to_match=rule_text,
                                map_to=map_to,
                                income_type=category if map_to == "Income" and category in INCOME_TYPES else None,
                                expense_category=category if map_to == "Expense" and category in EXPENSE_CATEGORIES else None,
                                priority=(added_count + 1) * 10,
                                enabled=True,
                                notes=f"Quick rule from {selected_category}"
                            )
                            session.add(new_rule)
                            added_count += 1
                    
                    session.commit()
                    show_toast(f"Added {added_count} new rules", "success")
                    if added_count < len(selected_rules):
                        show_toast(f"{len(selected_rules) - added_count} rules already existed", "warning")
                    st.rerun()
    
    # ============================================================================
    # TAB NAVIGATION
    # ============================================================================
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Rules", "➕ Add Rule", "🧪 Test Rules", "📊 Analytics"])
    
    with tab1:
        # ====================================================================
        # VIEW RULES TAB
        # ====================================================================
        
        st.subheader("📋 Current Rules")
        
        # Filter options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filter_status = st.selectbox("Status", ["All", "Active", "Disabled"])
        with col2:
            filter_type = st.selectbox("Type", ["All", "Income", "Expense", "Ignore"])
        with col3:
            filter_mode = st.selectbox("Match Mode", ["All"] + MATCH_MODES)
        with col4:
            search_text = st.text_input("🔍 Search", placeholder="Search rule text...")
        
        # Query rules
        query = session.query(Rule)
        
        if filter_status == "Active":
            query = query.filter(Rule.enabled == True)
        elif filter_status == "Disabled":
            query = query.filter(Rule.enabled == False)
        
        if filter_type != "All":
            query = query.filter(Rule.map_to == filter_type)
        
        if filter_mode != "All":
            query = query.filter(Rule.match_mode == filter_mode)
        
        if search_text:
            query = query.filter(Rule.text_to_match.contains(search_text))
        
        rules = query.order_by(Rule.priority).all()
        
        if rules:
            # Group rules by type for better visualization
            income_rules_list = [r for r in rules if r.map_to == "Income"]
            expense_rules_list = [r for r in rules if r.map_to == "Expense"]
            ignore_rules_list = [r for r in rules if r.map_to == "Ignore"]
            
            # Display rules by type
            for rule_type, rule_list, color in [
                ("💰 Income Rules", income_rules_list, "green"),
                ("💳 Expense Rules", expense_rules_list, "red"),
                ("🚫 Ignore Rules", ignore_rules_list, "gray")
            ]:
                if rule_list:
                    st.markdown(f"### {rule_type}")
                    
                    for rule in rule_list:
                        with st.container():
                            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 0.5, 0.5, 1])

                            with col1:
                                # Rule text with match mode
                                status_icon = "✅" if rule.enabled else "⏸️"
                                st.markdown(f"""
                                **{status_icon} {rule.text_to_match}**
                                *{rule.match_mode}* • Priority: {rule.priority} • ID: #{rule.id}
                                """)

                            with col2:
                                # Category/Type
                                category = rule.income_type or rule.expense_category or "N/A"
                                if category != "N/A":
                                    if color == "green":
                                        st.success(f"→ {category}")
                                    elif color == "red":
                                        st.error(f"→ {category}")
                                    else:
                                        st.info(f"→ Personal/Ignore")

                            with col3:
                                # Toggle enabled
                                new_status = st.checkbox(
                                    "Active",
                                    value=rule.enabled,
                                    key=f"toggle_{rule.id}"
                                )
                                if new_status != rule.enabled:
                                    rule.enabled = new_status
                                    session.commit()
                                    st.rerun()

                            with col4:
                                # Edit button
                                if st.button("✏️", key=f"edit_{rule.id}", help="Edit rule"):
                                    st.session_state['edit_rule_id'] = rule.id
                                    st.session_state['show_edit_form'] = True

                            with col5:
                                # Delete button
                                if st.button("🗑️", key=f"delete_{rule.id}", help="Delete rule"):
                                    session.delete(rule)
                                    session.commit()
                                    show_toast(f"Rule deleted: {rule.text_to_match}", "delete")
                                    st.rerun()

                            with col6:
                                # Test button
                                if st.button("Test", key=f"test_{rule.id}", help="Test against existing transactions"):
                                    st.session_state['test_rule_id'] = rule.id

                            if rule.notes:
                                st.caption(f"📝 {rule.notes}")

                            # Show test results for selected rule
                            if st.session_state.get('test_rule_id') == rule.id:
                                # Find matching transactions
                                test_rule = rule
                                import re as _re
                                matching_txns = []
                                all_txns = session.query(Transaction).all()
                                for txn in all_txns:
                                    desc = (txn.description or "").upper()
                                    rule_text = test_rule.text_to_match.upper()
                                    is_match = False
                                    if test_rule.match_mode == "Contains" and rule_text in desc:
                                        is_match = True
                                    elif test_rule.match_mode == "Equals" and desc == rule_text:
                                        is_match = True
                                    elif test_rule.match_mode == "Starts with" and desc.startswith(rule_text):
                                        is_match = True
                                    elif test_rule.match_mode == "Ends with" and desc.endswith(rule_text):
                                        is_match = True
                                    elif test_rule.match_mode == "Regex":
                                        try:
                                            if _re.search(test_rule.text_to_match, txn.description or "", _re.IGNORECASE):
                                                is_match = True
                                        except Exception:
                                            pass
                                    if is_match:
                                        matching_txns.append(txn)

                                match_count = len(matching_txns)
                                cat = test_rule.income_type or test_rule.expense_category or "Ignore"

                                if match_count > 0:
                                    st.markdown(f"""
                                    <div class="mr-chart-filter">
                                        <span class="filter-label">Rule "{test_rule.text_to_match}" matches</span>
                                        <span class="filter-value">{match_count} transactions</span>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Show first 10 matches
                                    with st.expander(f"View {min(match_count, 10)} of {match_count} matches", expanded=True):
                                        for txn in matching_txns[:10]:
                                            st.markdown(f"- **{txn.description}** — {txn.date.strftime('%d %b %Y')} — £{float(txn.amount or 0):,.2f}")

                                    # Apply button
                                    if st.button(f"Apply rule to all {match_count} matches", key=f"apply_rule_{rule.id}", type="primary"):
                                        applied = 0
                                        for txn in matching_txns:
                                            txn.guessed_type = test_rule.map_to
                                            txn.guessed_category = cat
                                            txn.confidence_score = 0.95
                                            applied += 1
                                        session.commit()
                                        show_toast(f"Rule applied to {applied} transactions", "success")
                                        st.session_state.pop('test_rule_id', None)
                                        st.rerun()
                                else:
                                    st.info(f"No existing transactions match \"{test_rule.text_to_match}\"")

                                if st.button("Close test results", key=f"close_test_{rule.id}"):
                                    st.session_state.pop('test_rule_id', None)
                                    st.rerun()

                            st.markdown("---")
            
            # Edit form (if triggered)
            if st.session_state.get('show_edit_form'):
                rule_id = st.session_state.get('edit_rule_id')
                rule = session.query(Rule).get(rule_id)
                
                if rule:
                    st.markdown("### ✏️ Edit Rule")
                    
                    with st.form("edit_rule_form"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            new_text = st.text_input("Text to Match", value=rule.text_to_match)
                            new_mode = st.selectbox("Match Mode", MATCH_MODES, 
                                                   index=MATCH_MODES.index(rule.match_mode))
                        
                        with col2:
                            new_map_to = st.selectbox("Map To", ["Income", "Expense", "Ignore"],
                                                     index=["Income", "Expense", "Ignore"].index(rule.map_to))
                            new_priority = st.number_input("Priority", value=rule.priority, min_value=1)
                        
                        with col3:
                            if new_map_to == "Income":
                                new_category = st.selectbox("Income Type", INCOME_TYPES,
                                                           index=INCOME_TYPES.index(rule.income_type) if rule.income_type in INCOME_TYPES else 0)
                            elif new_map_to == "Expense":
                                new_category = st.selectbox("Expense Category", EXPENSE_CATEGORIES,
                                                           index=EXPENSE_CATEGORIES.index(rule.expense_category) if rule.expense_category in EXPENSE_CATEGORIES else 0)
                            else:
                                new_category = None
                        
                        new_notes = st.text_area("Notes", value=rule.notes or "")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                rule.text_to_match = new_text
                                rule.match_mode = new_mode
                                rule.map_to = new_map_to
                                rule.priority = new_priority
                                rule.income_type = new_category if new_map_to == "Income" else None
                                rule.expense_category = new_category if new_map_to == "Expense" else None
                                rule.notes = new_notes
                                session.commit()
                                show_toast(f"Rule updated: {new_text}", "success")
                                st.session_state['show_edit_form'] = False
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state['show_edit_form'] = False
                                st.rerun()
        else:
            st.info("No rules found. Add your first rule to start automating categorization!")
    
    with tab2:
        # ====================================================================
        # ADD RULE TAB
        # ====================================================================
        
        st.subheader("➕ Add New Rule")
        
        with st.form("add_rule_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Matching Criteria")
                text_to_match = st.text_input(
                    "Text to Match",
                    placeholder="e.g., AMAZON, SPOTIFY, HMRC",
                    help="The text to search for in transaction descriptions"
                )
                
                match_mode = st.selectbox(
                    "Match Mode",
                    MATCH_MODES,
                    help="How to match the text"
                )
                
                priority = st.number_input(
                    "Priority",
                    min_value=1,
                    value=100,
                    step=10,
                    help="Lower numbers = higher priority"
                )
            
            with col2:
                st.markdown("#### Categorization")
                map_to = st.selectbox(
                    "Map To",
                    ["Income", "Expense", "Ignore"],
                    help="What type of transaction this is"
                )
                
                if map_to == "Income":
                    category = st.selectbox("Income Type", INCOME_TYPES)
                elif map_to == "Expense":
                    category = st.selectbox("Expense Category", EXPENSE_CATEGORIES)
                else:
                    category = None
                    st.info("Transactions will be marked as personal/ignored")
                
                enabled = st.checkbox("Enable rule immediately", value=True)
            
            notes = st.text_area(
                "Notes (optional)",
                placeholder="Any notes about this rule..."
            )
            
            # Show example of what this rule would match
            if text_to_match:
                st.info(f"""
                **Example matches for "{text_to_match}" ({match_mode}):**
                - {"✅" if match_mode == "Contains" else "❌"} "Payment to {text_to_match} Ltd"
                - {"✅" if match_mode in ["Contains", "Starts with"] else "❌"} "{text_to_match} Purchase"
                - {"✅" if match_mode == "Equals" else "❌"} "{text_to_match}"
                """)
            
            submitted = st.form_submit_button("➕ Create Rule", type="primary", use_container_width=True)
            
            if submitted:
                if text_to_match:
                    # Check for duplicate
                    existing = session.query(Rule).filter(
                        Rule.text_to_match == text_to_match,
                        Rule.match_mode == match_mode
                    ).first()
                    
                    if existing:
                        st.error(f"❌ Rule already exists with this text and match mode!")
                    else:
                        new_rule = Rule(
                            match_mode=match_mode,
                            text_to_match=text_to_match,
                            map_to=map_to,
                            income_type=category if map_to == "Income" else None,
                            expense_category=category if map_to == "Expense" else None,
                            priority=priority,
                            enabled=enabled,
                            notes=notes
                        )
                        session.add(new_rule)
                        session.commit()
                        show_toast(f"Rule created: {text_to_match} → {map_to}: {category if category else 'Ignore'}", "success")
                else:
                    st.error("❌ Please provide text to match")
    
    with tab3:
        # ====================================================================
        # TEST RULES TAB
        # ====================================================================
        
        st.subheader("🧪 Test Your Rules")
        st.markdown("See how your rules would categorize a transaction description")
        
        test_description = st.text_input(
            "Enter a transaction description to test",
            placeholder="e.g., TESCO STORES 2847 LONDON",
            help="Type or paste a transaction description to see which rule would match"
        )
        
        if test_description:
            # Find matching rules
            all_rules = session.query(Rule).filter(Rule.enabled == True).order_by(Rule.priority).all()
            
            matched_rule = None
            all_matches = []
            
            for rule in all_rules:
                text_upper = test_description.upper()
                rule_text_upper = rule.text_to_match.upper()
                
                is_match = False
                if rule.match_mode == "Contains" and rule_text_upper in text_upper:
                    is_match = True
                elif rule.match_mode == "Starts with" and text_upper.startswith(rule_text_upper):
                    is_match = True
                elif rule.match_mode == "Ends with" and text_upper.endswith(rule_text_upper):
                    is_match = True
                elif rule.match_mode == "Equals" and text_upper == rule_text_upper:
                    is_match = True
                elif rule.match_mode == "Regex":
                    import re
                    try:
                        if re.search(rule.text_to_match, test_description, re.IGNORECASE):
                            is_match = True
                    except:
                        pass
                
                if is_match:
                    all_matches.append(rule)
                    if not matched_rule:
                        matched_rule = rule
            
            # Display results
            if matched_rule:
                category = matched_rule.income_type or matched_rule.expense_category or "Personal/Ignore"
                
                st.success(f"""
                ✅ **Rule Match Found!**
                
                **Winning Rule:** "{matched_rule.text_to_match}" (Priority: {matched_rule.priority})  
                **Match Mode:** {matched_rule.match_mode}  
                **Categorization:** {matched_rule.map_to} → {category}
                """)
                
                if len(all_matches) > 1:
                    with st.expander(f"ℹ️ {len(all_matches) - 1} other rules also matched (lower priority)"):
                        for rule in all_matches[1:]:
                            cat = rule.income_type or rule.expense_category or "Personal/Ignore"
                            st.write(f"- \"{rule.text_to_match}\" → {rule.map_to}: {cat} (Priority: {rule.priority})")
            else:
                st.warning("""
                ❌ **No Matching Rules**
                
                This transaction would not be auto-categorized.  
                Consider adding a rule for this type of transaction.
                """)
                
                # Suggest a rule
                if st.button("➕ Create Rule for This"):
                    st.session_state['suggested_text'] = test_description.split()[0] if test_description else ""
                    st.info(f"Suggested rule text: {st.session_state['suggested_text']}")
    
    with tab4:
        # ====================================================================
        # ANALYTICS TAB
        # ====================================================================
        
        st.subheader("📊 Rule Analytics")
        
        # Rule effectiveness over time
        st.markdown("#### 📈 Auto-Categorization Trend")
        
        # Get monthly stats
        from datetime import datetime, timedelta
        
        months = []
        auto_rates = []
        
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            if month_date.month == 12:
                month_end = month_date.replace(year=month_date.year+1, month=1, day=1)
            else:
                month_end = month_date.replace(month=month_date.month+1, day=1)
            
            month_total = session.query(func.count(Transaction.id)).filter(
                Transaction.date >= month_start,
                Transaction.date < month_end
            ).scalar() or 0
            
            month_auto = session.query(func.count(Transaction.id)).filter(
                Transaction.date >= month_start,
                Transaction.date < month_end,
                Transaction.confidence_score > 0
            ).scalar() or 0
            
            if month_total > 0:
                months.append(month_date.strftime('%b %Y'))
                auto_rates.append((month_auto / month_total) * 100)
        
        if auto_rates:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(reversed(months)),
                y=list(reversed(auto_rates)),
                mode='lines+markers',
                name='Auto-categorization Rate',
                line=dict(color='#36c7a0', width=3),
                marker=dict(size=10),
                fill='tonexty',
                fillcolor='rgba(54, 199, 160, 0.1)'
            ))
            
            fig.update_layout(
                height=300,
                showlegend=False,
                plot_bgcolor='#12161f',
                paper_bgcolor='#12161f',
                yaxis=dict(
                    title=dict(text='Auto-categorization %', font=dict(color='#c8cdd5')),
                    tickfont=dict(color='#c8cdd5'),
                    range=[0, 100],
                    showgrid=True,
                    gridcolor='rgba(79, 143, 234, 0.08)'
                ),
                xaxis=dict(
                    title='',
                    tickfont=dict(color='#c8cdd5'),
                    showgrid=False
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Most effective rules
        st.markdown("#### 🏆 Most Used Rules")
        
        # This would need a way to track rule usage, for now show all rules by priority
        top_rules = session.query(Rule).filter(Rule.enabled == True).order_by(Rule.priority).limit(10).all()
        
        if top_rules:
            for i, rule in enumerate(top_rules, 1):
                category = rule.income_type or rule.expense_category or "Personal/Ignore"
                col1, col2, col3 = st.columns([0.5, 3, 1])
                
                with col1:
                    st.markdown(f"**#{i}**")
                with col2:
                    st.write(f"**{rule.text_to_match}** ({rule.match_mode})")
                with col3:
                    st.write(f"→ {category}")
        
        # Suggestions for improvement
        st.markdown("#### 💡 Optimization Suggestions")
        
        # Check for potential issues
        suggestions = []
        
        # Check for duplicate priorities
        priority_counts = session.query(
            Rule.priority, 
            func.count(Rule.id).label('count')
        ).group_by(Rule.priority).having(func.count(Rule.id) > 1).all()
        
        if priority_counts:
            suggestions.append(f"⚠️ **Duplicate Priorities**: {len(priority_counts)} priority values are used by multiple rules. Consider spacing them out.")
        
        # Check for disabled rules
        if total_rules - active_rules > 0:
            suggestions.append(f"ℹ️ **Disabled Rules**: You have {total_rules - active_rules} disabled rules. Consider removing them if no longer needed.")
        
        # Check for very generic rules
        generic_rules = session.query(Rule).filter(
            Rule.match_mode == "Contains",
            func.length(Rule.text_to_match) <= 3
        ).all()
        
        if generic_rules:
            suggestions.append(f"⚠️ **Very Short Rules**: {len(generic_rules)} rules have 3 or fewer characters. These might match too many transactions.")
        
        if suggestions:
            for suggestion in suggestions:
                st.info(suggestion)
        else:
            st.success("✅ Your rules are well-optimized!")
        
        # Export/Import section
        st.markdown("#### 💾 Backup & Restore")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Rules to CSV", use_container_width=True):
                rules_data = []
                for rule in session.query(Rule).all():
                    rules_data.append({
                        'Priority': rule.priority,
                        'Match Mode': rule.match_mode,
                        'Text to Match': rule.text_to_match,
                        'Map To': rule.map_to,
                        'Category': rule.income_type or rule.expense_category or '',
                        'Enabled': rule.enabled,
                        'Notes': rule.notes or ''
                    })
                
                df = pd.DataFrame(rules_data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="💾 Download Rules CSV",
                    data=csv,
                    file_name=f"categorization_rules_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.info("📤 Import from CSV coming soon!")
