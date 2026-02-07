"""
Restructured Mileage Screen with Modern Interface Design
Complete UI overhaul for mileage tracking and management
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
import plotly.graph_objects as go
import plotly.express as px
from models import Mileage
from utils import format_currency, get_tax_year_dates, calculate_mileage_allowance

def render_restructured_mileage_screen(session, settings):
    """
    Render a completely restructured mileage management interface
    """
    
    # Get tax year
    tax_year = settings.get('tax_year', '2024/25')
    start_date, end_date = get_tax_year_dates(tax_year)
    
    # ============================================================================
    # HEADER SECTION
    # ============================================================================
    st.markdown("# 🚗 Business Mileage")
    st.markdown(f"**Track your business journeys and claim mileage allowance for tax year {tax_year}**")
    
    # ============================================================================
    # HMRC RATES INFORMATION
    # ============================================================================
    st.info(f"""
    💡 **HMRC Mileage Rates for {tax_year}**
    
    First 10,000 miles: **45p per mile** | After 10,000 miles: **25p per mile**
    """)
    
    # ============================================================================
    # QUICK STATS OVERVIEW
    # ============================================================================
    
    # Calculate key metrics
    total_miles = session.query(func.sum(Mileage.miles)).filter(
        and_(Mileage.date >= start_date, Mileage.date <= end_date)
    ).scalar() or 0.0
    
    total_allowance = session.query(func.sum(Mileage.allowable_amount)).filter(
        and_(Mileage.date >= start_date, Mileage.date <= end_date)
    ).scalar() or 0.0
    
    journey_count = session.query(func.count(Mileage.id)).filter(
        and_(Mileage.date >= start_date, Mileage.date <= end_date)
    ).scalar() or 0
    
    # Calculate average miles per journey
    avg_miles = total_miles / journey_count if journey_count > 0 else 0
    
    # Calculate effective rate
    effective_rate = total_allowance / total_miles if total_miles > 0 else 0.45
    
    # Display stats in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Miles",
            value=f"{total_miles:,.0f}",
            help="Total business miles traveled this tax year"
        )
    
    with col2:
        st.metric(
            label="Total Claim",
            value=format_currency(total_allowance),
            help="Total claimable mileage allowance"
        )
    
    with col3:
        st.metric(
            label="Journeys",
            value=f"{journey_count}",
            help="Number of business journeys"
        )
    
    with col4:
        st.metric(
            label="Avg Miles",
            value=f"{avg_miles:.0f}",
            help="Average miles per journey"
        )
    
    with col5:
        st.metric(
            label="Avg Rate",
            value=f"{effective_rate:.2f}p",
            help="Average rate per mile"
        )
    
    st.markdown("---")
    
    # ============================================================================
    # TAB NAVIGATION
    # ============================================================================
    
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Journeys", "➕ Add Journey", "📊 Analytics", "⚙️ Manage"])
    
    with tab1:
        # ====================================================================
        # JOURNEYS TAB
        # ====================================================================
        
        st.subheader("🗺️ Recent Business Journeys")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            date_filter = st.selectbox(
                "Date Range",
                ["This Month", "Last Month", "Last 3 Months", "This Tax Year", "Custom"]
            )
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Date (Newest)", "Date (Oldest)", "Miles (High)", "Miles (Low)", "Amount (High)"]
            )
        with col3:
            search_term = st.text_input("🔍 Search", placeholder="Search purpose or location...")
        
        # Query journeys
        query = session.query(Mileage).filter(
            and_(Mileage.date >= start_date, Mileage.date <= end_date)
        )
        
        # Apply search filter
        if search_term:
            query = query.filter(
                Mileage.purpose.contains(search_term) |
                Mileage.from_location.contains(search_term) |
                Mileage.to_location.contains(search_term)
            )
        
        # Apply date filter
        if date_filter == "This Month":
            month_start = datetime.now().replace(day=1)
            query = query.filter(Mileage.date >= month_start)
        elif date_filter == "Last Month":
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            month_start = last_month.replace(day=1)
            month_end = datetime.now().replace(day=1)
            query = query.filter(and_(Mileage.date >= month_start, Mileage.date < month_end))
        elif date_filter == "Last 3 Months":
            three_months_ago = datetime.now() - timedelta(days=90)
            query = query.filter(Mileage.date >= three_months_ago)
        
        # Apply sorting
        if sort_by == "Date (Newest)":
            query = query.order_by(Mileage.date.desc())
        elif sort_by == "Date (Oldest)":
            query = query.order_by(Mileage.date.asc())
        elif sort_by == "Miles (High)":
            query = query.order_by(Mileage.miles.desc())
        elif sort_by == "Miles (Low)":
            query = query.order_by(Mileage.miles.asc())
        elif sort_by == "Amount (High)":
            query = query.order_by(Mileage.allowable_amount.desc())
        
        journeys = query.limit(20).all()
        
        if journeys:
            # Monthly summary
            current_month_miles = sum(j.miles for j in journeys if j.date.month == datetime.now().month)
            current_month_amount = sum(j.allowable_amount for j in journeys if j.date.month == datetime.now().month)
            
            if current_month_miles > 0:
                st.info(f"""
                **{datetime.now().strftime('%B %Y')} Summary**
                
                {current_month_miles:.0f} miles traveled • {format_currency(current_month_amount)} claimable
                """)
            
            # Display journey cards
            for journey in journeys:
                # Determine rate used
                rate_badge = "45p/mile" if journey.rate_per_mile >= 0.45 else "25p/mile"
                rate_color = ":green" if journey.rate_per_mile >= 0.45 else ":orange"
                
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### {journey.purpose}")
                        
                        # Route display
                        route_text = f"📍 **{journey.from_location or 'Start'}** → 📍 **{journey.to_location or 'End'}**"
                        st.markdown(route_text)
                        
                        # Details
                        st.caption(f"""
                        📅 {journey.date.strftime('%d %B %Y')} • 
                        {rate_badge} • 
                        ID: #{journey.id}
                        """)
                        
                        if journey.notes:
                            st.caption(f"📝 {journey.notes}")
                    
                    with col2:
                        st.metric("Miles", f"{journey.miles:.1f}")
                        st.metric("Claimable", format_currency(journey.allowable_amount))
                
                st.markdown("---")
        else:
            st.info("No journeys found for the selected criteria")
    
    with tab2:
        # ====================================================================
        # ADD JOURNEY TAB
        # ====================================================================
        
        st.subheader("➕ Add New Business Journey")
        
        # Quick templates
        st.markdown("#### Quick Templates")
        col1, col2, col3, col4 = st.columns(4)
        
        template = None
        with col1:
            if st.button("👥 Client Meeting", use_container_width=True):
                st.session_state['mileage_template'] = "client"
        with col2:
            if st.button("🏪 Supplier Visit", use_container_width=True):
                st.session_state['mileage_template'] = "supplier"
        with col3:
            if st.button("🏦 Bank/Office", use_container_width=True):
                st.session_state['mileage_template'] = "office"
        with col4:
            if st.button("📦 Delivery", use_container_width=True):
                st.session_state['mileage_template'] = "delivery"
        
        # Set defaults based on template
        template = st.session_state.get('mileage_template', None)
        if template == "client":
            default_purpose = "Client meeting"
        elif template == "supplier":
            default_purpose = "Supplier visit"
        elif template == "office":
            default_purpose = "Office/Bank visit"
        elif template == "delivery":
            default_purpose = "Delivery/Collection"
        else:
            default_purpose = ""
        
        st.markdown("#### Journey Details")
        
        with st.form("add_mileage_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                journey_date = st.date_input("📅 Date", value=datetime.now())
                journey_purpose = st.text_input("💼 Purpose", placeholder="e.g., Client meeting", value=default_purpose)
                journey_from = st.text_input("📍 From Location", placeholder="e.g., Home Office")
            
            with col2:
                journey_to = st.text_input("📍 To Location", placeholder="e.g., Client Office, London")
                journey_miles = st.number_input("🚗 Miles", min_value=0.0, step=0.1)
                
                # Determine rate based on total miles so far
                if total_miles < 10000:
                    default_rate = 0.45
                    rate_info = "First 10,000 miles rate"
                else:
                    default_rate = 0.25
                    rate_info = "Over 10,000 miles rate"
                
                journey_rate = st.number_input(f"💷 Rate per Mile ({rate_info})", value=default_rate, step=0.01)
            
            journey_notes = st.text_area("📝 Notes (optional)", placeholder="Any additional information...")
            
            # Calculate allowance
            calculated_allowance = journey_miles * journey_rate
            
            # Display calculation
            st.success(f"""
            **Calculation Summary**
            
            {journey_miles:.1f} miles × {journey_rate:.2f}p/mile = **{format_currency(calculated_allowance)}** claimable
            """)
            
            submitted = st.form_submit_button("🚗 Save Journey", type="primary", use_container_width=True)
            
            if submitted:
                if journey_purpose and journey_miles > 0:
                    new_journey = Mileage(
                        date=journey_date,
                        purpose=journey_purpose,
                        from_location=journey_from,
                        to_location=journey_to,
                        miles=journey_miles,
                        rate_per_mile=journey_rate,
                        allowable_amount=calculated_allowance,
                        notes=journey_notes
                    )
                    session.add(new_journey)
                    session.commit()
                    st.success(f"✅ Journey added! Claimable amount: {format_currency(calculated_allowance)}")
                    st.balloons()
                else:
                    st.error("❌ Please provide purpose and miles")
    
    with tab3:
        # ====================================================================
        # ANALYTICS TAB
        # ====================================================================
        
        st.subheader("📊 Mileage Analytics")
        
        # Monthly mileage chart
        st.markdown("#### 📈 Monthly Mileage Trend")
        
        # Get monthly data
        monthly_mileage = session.query(
            extract('month', Mileage.date).label('month'),
            extract('year', Mileage.date).label('year'),
            func.sum(Mileage.miles).label('miles'),
            func.sum(Mileage.allowable_amount).label('amount')
        ).filter(
            and_(Mileage.date >= start_date, Mileage.date <= end_date)
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        if monthly_mileage:
            # Create dual-axis chart
            months = []
            miles_data = []
            amount_data = []
            
            for record in monthly_mileage:
                month_name = datetime(int(record.year), int(record.month), 1).strftime('%b %Y')
                months.append(month_name)
                miles_data.append(float(record.miles))
                amount_data.append(float(record.amount))
            
            fig = go.Figure()
            
            # Miles bar chart
            fig.add_trace(go.Bar(
                name='Miles',
                x=months,
                y=miles_data,
                yaxis='y',
                marker_color='#3b82f6',
                text=[f'{m:.0f}' for m in miles_data],
                textposition='outside'
            ))
            
            # Allowance line chart
            fig.add_trace(go.Scatter(
                name='Allowance (£)',
                x=months,
                y=amount_data,
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#10b981', width=3),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                height=400,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(
                    title='Miles',
                    showgrid=True,
                    gridcolor='#f0f0f0'
                ),
                yaxis2=dict(
                    title='Allowance (£)',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                xaxis=dict(
                    title='',
                    showgrid=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for chart")
        
        # Purpose breakdown
        st.markdown("#### 🎯 Journey Purpose Breakdown")
        
        purpose_breakdown = session.query(
            Mileage.purpose,
            func.count(Mileage.id).label('count'),
            func.sum(Mileage.miles).label('total_miles'),
            func.sum(Mileage.allowable_amount).label('total_amount')
        ).filter(
            and_(Mileage.date >= start_date, Mileage.date <= end_date)
        ).group_by(Mileage.purpose).order_by(func.sum(Mileage.miles).desc()).limit(10).all()
        
        if purpose_breakdown:
            # Create treemap
            fig_treemap = go.Figure(go.Treemap(
                labels=[p[0][:30] for p in purpose_breakdown],
                values=[float(p[2]) for p in purpose_breakdown],
                parents=[""] * len(purpose_breakdown),
                text=[f"{p[0]}<br>{p[2]:.0f} miles<br>{p[1]} journeys<br>£{p[3]:.2f}" for p in purpose_breakdown],
                marker=dict(
                    colorscale='Blues',
                    cmid=50
                )
            ))
            
            fig_treemap.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.info("No journey data available")
        
        # Rate analysis
        st.markdown("#### 💷 Rate Analysis")
        
        miles_at_45p = min(total_miles, 10000)
        miles_at_25p = max(0, total_miles - 10000)
        amount_at_45p = miles_at_45p * 0.45
        amount_at_25p = miles_at_25p * 0.25
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **First 10,000 miles @ 45p**
            - Miles: {miles_at_45p:,.0f}
            - Amount: {format_currency(amount_at_45p)}
            
            **After 10,000 miles @ 25p**
            - Miles: {miles_at_25p:,.0f}
            - Amount: {format_currency(amount_at_25p)}
            """)
        
        with col2:
            # Progress to 10,000 miles
            progress_to_10k = min(100, (total_miles / 10000) * 100)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = total_miles,
                title = {'text': "Progress to 10,000 miles"},
                delta = {'reference': 10000},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 10000]},
                    'bar': {'color': "#3b82f6"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e0e7ff",
                    'steps': [
                        {'range': [0, 5000], 'color': '#dbeafe'},
                        {'range': [5000, 10000], 'color': '#bfdbfe'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 10000
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with tab4:
        # ====================================================================
        # MANAGE TAB
        # ====================================================================
        
        st.subheader("⚙️ Manage Journey Records")
        
        # Get all journeys for management
        all_journeys = session.query(Mileage).filter(
            and_(Mileage.date >= start_date, Mileage.date <= end_date)
        ).order_by(Mileage.date.desc()).all()
        
        if all_journeys:
            st.info(f"Total: {len(all_journeys)} journeys")
            
            # Edit/Delete section
            st.markdown("#### ✏️ Edit or Delete Journey")
            
            journey_id = st.number_input("Enter Journey ID", min_value=1, step=1, key="mileage_edit_id")
            
            if journey_id:
                journey = session.query(Mileage).filter(Mileage.id == journey_id).first()
                
                if journey:
                    st.success(f"Selected Journey: {journey.purpose} - {journey.date.strftime('%d %b %Y')} - {journey.miles:.1f} miles")
                    
                    action = st.radio("Select Action", ["Edit", "Delete"], horizontal=True)
                    
                    if action == "Edit":
                        with st.form("edit_mileage_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_date = st.date_input("Date", value=journey.date)
                                new_purpose = st.text_input("Purpose", value=journey.purpose)
                                new_from = st.text_input("From Location", value=journey.from_location or '')
                            
                            with col2:
                                new_to = st.text_input("To Location", value=journey.to_location or '')
                                new_miles = st.number_input("Miles", value=float(journey.miles), step=0.1)
                                new_rate = st.number_input("Rate per Mile", value=float(journey.rate_per_mile), step=0.01)
                            
                            new_notes = st.text_area("Notes", value=journey.notes or '')
                            
                            if st.form_submit_button("💾 Update Journey", type="primary"):
                                journey.date = new_date
                                journey.purpose = new_purpose
                                journey.from_location = new_from
                                journey.to_location = new_to
                                journey.miles = new_miles
                                journey.rate_per_mile = new_rate
                                journey.allowable_amount = new_miles * new_rate
                                journey.notes = new_notes
                                session.commit()
                                st.success("✅ Journey updated successfully!")
                                st.rerun()
                    
                    elif action == "Delete":
                        st.warning("⚠️ This action cannot be undone!")
                        if st.button("🗑️ Delete Journey", type="secondary"):
                            session.delete(journey)
                            session.commit()
                            st.success("✅ Journey deleted successfully!")
                            st.rerun()
                else:
                    st.error("❌ Journey not found")
            
            # Export functionality
            st.markdown("#### 📥 Export Mileage Log")
            
            if st.button("📊 Generate Mileage Report", use_container_width=True):
                # Create DataFrame for export
                data = []
                for j in all_journeys:
                    data.append({
                        'Date': j.date.strftime('%Y-%m-%d'),
                        'Purpose': j.purpose,
                        'From': j.from_location or '',
                        'To': j.to_location or '',
                        'Miles': j.miles,
                        'Rate': j.rate_per_mile,
                        'Amount': j.allowable_amount,
                        'Notes': j.notes or ''
                    })
                
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"mileage_log_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No journey records found")
