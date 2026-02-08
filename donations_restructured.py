"""
Restructured Donations Screen with Modern Interface Design
Complete UI overhaul for Gift Aid donations tracking
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
import plotly.graph_objects as go
import plotly.express as px
from models import Donation
from utils import format_currency, get_tax_year_dates
from components.ui.interactions import show_toast, confirm_delete, validate_field, show_validation

def render_restructured_donations_screen(session, settings):
    """
    Render a completely restructured donations management interface
    """
    
    # Get tax year
    tax_year = settings.get('tax_year', '2024/25')
    start_date, end_date = get_tax_year_dates(tax_year)
    
    # ============================================================================
    # HEADER SECTION
    # ============================================================================
    st.markdown("# 🎁 Gift Aid Donations")
    st.markdown(f"**Track charitable donations for Gift Aid relief in tax year {tax_year}**")
    
    # ============================================================================
    # GIFT AID INFORMATION
    # ============================================================================
    st.info("""
    💡 **How Gift Aid Works**
    
    When you donate to charity through Gift Aid:
    - The charity can claim an extra 25p for every £1 you donate
    - If you're a higher rate taxpayer, you can claim back the difference between the higher rate (40% or 45%) and basic rate (20%) on your donation
    - For example: On a £100 donation, the charity gets £125, and you can claim back £25 (40% taxpayer) or £31.25 (45% taxpayer)
    """)
    
    # ============================================================================
    # QUICK STATS OVERVIEW
    # ============================================================================
    
    # Calculate key metrics
    total_donated = session.query(func.sum(Donation.amount_paid)).filter(
        and_(
            Donation.date >= start_date, 
            Donation.date <= end_date,
            Donation.gift_aid == True
        )
    ).scalar() or 0.0
    
    total_donated_all = session.query(func.sum(Donation.amount_paid)).filter(
        and_(Donation.date >= start_date, Donation.date <= end_date)
    ).scalar() or 0.0
    
    donation_count = session.query(func.count(Donation.id)).filter(
        and_(Donation.date >= start_date, Donation.date <= end_date)
    ).scalar() or 0
    
    gift_aid_count = session.query(func.count(Donation.id)).filter(
        and_(
            Donation.date >= start_date, 
            Donation.date <= end_date,
            Donation.gift_aid == True
        )
    ).scalar() or 0
    
    # Calculate tax relief (assuming 40% taxpayer for illustration)
    charity_receives = total_donated * 1.25  # Charity gets 25% extra
    tax_relief_40 = total_donated * 0.25  # 40% taxpayer can claim back 25%
    tax_relief_45 = total_donated * 0.3125  # 45% taxpayer can claim back 31.25%
    
    # Get unique charities count
    unique_charities = session.query(func.count(func.distinct(Donation.charity))).filter(
        and_(Donation.date >= start_date, Donation.date <= end_date)
    ).scalar() or 0
    
    # Display stats in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Donated",
            value=format_currency(total_donated_all),
            delta=f"{donation_count} donations",
            help="Total amount donated to all charities"
        )
    
    with col2:
        st.metric(
            label="Gift Aid Donations",
            value=format_currency(total_donated),
            delta=f"{gift_aid_count} eligible",
            help="Donations eligible for Gift Aid"
        )
    
    with col3:
        st.metric(
            label="Charities Receive",
            value=format_currency(charity_receives),
            delta=f"+{format_currency(charity_receives - total_donated)}",
            help="Total amount charities receive including Gift Aid"
        )
    
    with col4:
        st.metric(
            label="Your Tax Relief (40%)",
            value=format_currency(tax_relief_40),
            help="Amount you can claim back as a 40% taxpayer"
        )
    
    with col5:
        st.metric(
            label="Charities Supported",
            value=f"{unique_charities}",
            help="Number of different charities you've supported"
        )
    
    st.markdown("---")
    
    # ============================================================================
    # TAX RELIEF CALCULATOR
    # ============================================================================
    with st.expander("💰 **Calculate Your Tax Relief**", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            calc_amount = st.number_input(
                "Donation Amount (£)", 
                min_value=0.0, 
                value=100.0, 
                step=10.0,
                help="Enter the amount you donated"
            )
        
        with col2:
            tax_rate = st.selectbox(
                "Your Tax Rate",
                ["20% (Basic)", "40% (Higher)", "45% (Additional)"],
                index=1,
                help="Select your income tax rate"
            )
        
        with col3:
            if calc_amount > 0:
                charity_gets = calc_amount * 1.25
                
                if "40%" in tax_rate:
                    your_relief = calc_amount * 0.25
                elif "45%" in tax_rate:
                    your_relief = calc_amount * 0.3125
                else:
                    your_relief = 0
                
                st.markdown("**Results:**")
                st.success(f"""
                Charity receives: **{format_currency(charity_gets)}**  
                Your tax relief: **{format_currency(your_relief)}**  
                Net cost to you: **{format_currency(calc_amount - your_relief)}**
                """)
    
    # ============================================================================
    # TAB NAVIGATION
    # ============================================================================
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Donations", "➕ Add Donation", "📊 Analytics", "⚙️ Manage"])
    
    with tab1:
        # ====================================================================
        # VIEW DONATIONS TAB
        # ====================================================================
        
        st.subheader("📋 Donation Records")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_period = st.selectbox(
                "Time Period",
                ["This Tax Year", "This Month", "Last Month", "Last 3 Months", "Custom"]
            )
        with col2:
            filter_gift_aid = st.selectbox(
                "Gift Aid Status",
                ["All", "Gift Aid Only", "Non-Gift Aid Only"]
            )
        with col3:
            search_charity = st.text_input("🔍 Search Charity", placeholder="Search by name...")
        
        # Query donations
        query = session.query(Donation).filter(
            and_(Donation.date >= start_date, Donation.date <= end_date)
        )
        
        # Apply filters
        if filter_period == "This Month":
            month_start = datetime.now().replace(day=1)
            query = query.filter(Donation.date >= month_start)
        elif filter_period == "Last Month":
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            month_start = last_month.replace(day=1)
            month_end = datetime.now().replace(day=1)
            query = query.filter(and_(Donation.date >= month_start, Donation.date < month_end))
        elif filter_period == "Last 3 Months":
            three_months_ago = datetime.now() - timedelta(days=90)
            query = query.filter(Donation.date >= three_months_ago)
        
        if filter_gift_aid == "Gift Aid Only":
            query = query.filter(Donation.gift_aid == True)
        elif filter_gift_aid == "Non-Gift Aid Only":
            query = query.filter(Donation.gift_aid == False)
        
        if search_charity:
            query = query.filter(Donation.charity.contains(search_charity))
        
        donations = query.order_by(Donation.date.desc()).all()
        
        if donations:
            # Summary for filtered results
            filtered_total = sum(d.amount_paid for d in donations)
            filtered_gift_aid = sum(d.amount_paid for d in donations if d.gift_aid)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Filtered Results:** {len(donations)} donations totaling {format_currency(filtered_total)}")
            with col2:
                if filtered_gift_aid > 0:
                    st.success(f"**Gift Aid Eligible:** {format_currency(filtered_gift_aid)} ({format_currency(filtered_gift_aid * 0.25)} tax relief at 40%)")
            
            # Display donation cards
            for donation in donations:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Charity name with Gift Aid badge
                        if donation.gift_aid:
                            st.markdown(f"### {donation.charity} ✅")
                            gift_aid_text = "Gift Aid eligible"
                            charity_gets = donation.amount_paid * 1.25
                        else:
                            st.markdown(f"### {donation.charity}")
                            gift_aid_text = "No Gift Aid"
                            charity_gets = donation.amount_paid
                        
                        # Details
                        st.caption(f"""
                        📅 {donation.date.strftime('%d %B %Y')} • 
                        {gift_aid_text} • 
                        Charity receives: {format_currency(charity_gets)} •
                        ID: #{donation.id}
                        """)
                        
                        if donation.notes:
                            st.caption(f"📝 {donation.notes}")
                    
                    with col2:
                        st.metric("You Donated", format_currency(donation.amount_paid))
                        if donation.gift_aid:
                            st.caption(f"Tax relief (40%): {format_currency(donation.amount_paid * 0.25)}")
                
                st.markdown("---")
        else:
            st.info("No donations found for the selected criteria")
    
    with tab2:
        # ====================================================================
        # ADD DONATION TAB
        # ====================================================================
        
        st.subheader("➕ Add New Donation")
        
        # Quick templates for common charities
        st.markdown("#### Quick Add - Popular Charities")
        
        col1, col2, col3, col4 = st.columns(4)
        
        template = None
        with col1:
            if st.button("🏥 NHS Charities", use_container_width=True):
                st.session_state['charity_template'] = "NHS Charities Together"
        with col2:
            if st.button("🔴 British Red Cross", use_container_width=True):
                st.session_state['charity_template'] = "British Red Cross"
        with col3:
            if st.button("🦮 Guide Dogs", use_container_width=True):
                st.session_state['charity_template'] = "Guide Dogs for the Blind"
        with col4:
            if st.button("🎗️ Cancer Research", use_container_width=True):
                st.session_state['charity_template'] = "Cancer Research UK"
        
        # Get template if selected
        template_charity = st.session_state.get('charity_template', '')
        
        st.markdown("#### Donation Details")
        
        with st.form("add_donation_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                donation_date = st.date_input("📅 Date", value=datetime.now())
                charity_name = st.text_input(
                    "🏛️ Charity Name", 
                    placeholder="e.g., British Red Cross",
                    value=template_charity
                )
                donation_amount = st.number_input("💰 Amount Donated (£)", min_value=0.0, step=1.0)
            
            with col2:
                gift_aid = st.checkbox("✅ Gift Aid Declaration", value=True, help="Tick if you've made a Gift Aid declaration")
                donation_method = st.selectbox("💳 Payment Method", ["Bank Transfer", "Credit Card", "Cash", "Cheque", "Other"])
                reference = st.text_input("🔖 Reference (optional)", placeholder="e.g., Monthly donation")
            
            notes = st.text_area("📝 Notes (optional)", placeholder="Any additional information...")
            
            # Show calculation if Gift Aid is selected
            if gift_aid and donation_amount > 0:
                st.success(f"""
                **Gift Aid Summary**
                - You donate: {format_currency(donation_amount)}
                - Charity claims from HMRC: {format_currency(donation_amount * 0.25)}
                - **Charity receives total: {format_currency(donation_amount * 1.25)}**
                - Your tax relief (40% taxpayer): {format_currency(donation_amount * 0.25)}
                - Your tax relief (45% taxpayer): {format_currency(donation_amount * 0.3125)}
                """)
            
            submitted = st.form_submit_button("💝 Save Donation", type="primary", use_container_width=True)
            
            if submitted:
                v_charity = validate_field(charity_name, required=True, min_length=2, label="Charity name")
                v_amount = validate_field(donation_amount, required=True, min_value=0.01, label="Amount")
                errors = [e for ok, e in [v_charity, v_amount] if not ok]
                if errors:
                    for err in errors:
                        show_validation(False, err)
                else:
                    new_donation = Donation(
                        date=donation_date,
                        charity=charity_name,
                        amount_paid=donation_amount,
                        gift_aid=gift_aid,
                        notes=f"{donation_method}: {reference}. {notes}" if reference else f"{donation_method}. {notes}"
                    )
                    session.add(new_donation)
                    session.commit()
                    ga_label = " (Gift Aid)" if gift_aid else ""
                    show_toast(f"Donation saved — {format_currency(donation_amount)} to {charity_name}{ga_label}", "success")
    
    with tab3:
        # ====================================================================
        # ANALYTICS TAB
        # ====================================================================
        
        st.subheader("📊 Donation Analytics")
        
        # Get donation data for analytics
        all_donations = session.query(Donation).filter(
            and_(Donation.date >= start_date, Donation.date <= end_date)
        ).all()
        
        if all_donations:
            # Monthly donations chart
            st.markdown("#### 📈 Monthly Donation Trend")
            
            monthly_donations = session.query(
                extract('month', Donation.date).label('month'),
                extract('year', Donation.date).label('year'),
                func.sum(Donation.amount_paid).label('total'),
                func.count(Donation.id).label('count')
            ).filter(
                and_(Donation.date >= start_date, Donation.date <= end_date)
            ).group_by('year', 'month').order_by('year', 'month').all()
            
            if monthly_donations:
                months = []
                amounts = []
                counts = []
                
                for record in monthly_donations:
                    month_name = datetime(int(record.year), int(record.month), 1).strftime('%b %Y')
                    months.append(month_name)
                    amounts.append(float(record.total))
                    counts.append(record.count)
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Amount Donated',
                    x=months,
                    y=amounts,
                    marker_color='#8b5cf6',
                    text=[f'£{a:,.0f}' for a in amounts],
                    textposition='outside'
                ))
                
                fig.add_trace(go.Scatter(
                    name='Number of Donations',
                    x=months,
                    y=counts,
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(color='#ec4899', width=3),
                    marker=dict(size=10)
                ))
                
                fig.update_layout(
                    height=400,
                    hovermode='x unified',
                    plot_bgcolor='#12161f',
                    paper_bgcolor='#12161f',
                    yaxis=dict(
                        title=dict(text='Amount (£)', font=dict(color='#c8cdd5')),
                        tickfont=dict(color='#c8cdd5'),
                        showgrid=True,
                        gridcolor='rgba(79, 143, 234, 0.08)'
                    ),
                    yaxis2=dict(
                        title=dict(text='Number of Donations', font=dict(color='#c8cdd5')),
                        tickfont=dict(color='#c8cdd5'),
                        overlaying='y',
                        side='right'
                    ),
                    xaxis=dict(title='', tickfont=dict(color='#c8cdd5')),
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Charity breakdown
            st.markdown("#### 🏛️ Top Charities Supported")
            
            charity_breakdown = session.query(
                Donation.charity,
                func.sum(Donation.amount_paid).label('total'),
                func.count(Donation.id).label('count')
            ).filter(
                and_(Donation.date >= start_date, Donation.date <= end_date)
            ).group_by(Donation.charity).order_by(func.sum(Donation.amount_paid).desc()).all()
            
            if charity_breakdown:
                # Create pie chart
                fig_pie = go.Figure(data=[go.Pie(
                    labels=[c[0][:30] for c in charity_breakdown],
                    values=[float(c[1]) for c in charity_breakdown],
                    hole=.4,
                    marker=dict(colors=px.colors.sequential.Purples_r),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Total: £%{value:,.2f}<br>Donations: %{customdata}<br>Percentage: %{percent}<extra></extra>',
                    customdata=[c[2] for c in charity_breakdown]
                )])
                
                fig_pie.update_layout(
                    height=400,
                    showlegend=True,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Gift Aid vs Non-Gift Aid
            st.markdown("#### ✅ Gift Aid Analysis")
            
            gift_aid_stats = session.query(
                Donation.gift_aid,
                func.sum(Donation.amount_paid).label('total'),
                func.count(Donation.id).label('count')
            ).filter(
                and_(Donation.date >= start_date, Donation.date <= end_date)
            ).group_by(Donation.gift_aid).all()
            
            if gift_aid_stats:
                col1, col2, col3 = st.columns(3)
                
                gift_aid_total = sum(s[1] for s in gift_aid_stats if s[0])
                non_gift_aid_total = sum(s[1] for s in gift_aid_stats if not s[0])
                gift_aid_count = sum(s[2] for s in gift_aid_stats if s[0])
                non_gift_aid_count = sum(s[2] for s in gift_aid_stats if not s[0])
                
                with col1:
                    st.info(f"""
                    **Gift Aid Donations**
                    - Amount: {format_currency(gift_aid_total)}
                    - Count: {gift_aid_count}
                    - Charity bonus: {format_currency(gift_aid_total * 0.25)}
                    """)
                
                with col2:
                    st.warning(f"""
                    **Non-Gift Aid Donations**
                    - Amount: {format_currency(non_gift_aid_total)}
                    - Count: {non_gift_aid_count}
                    - No tax benefits
                    """)
                
                with col3:
                    st.success(f"""
                    **Tax Relief Available**
                    - At 40% rate: {format_currency(gift_aid_total * 0.25)}
                    - At 45% rate: {format_currency(gift_aid_total * 0.3125)}
                    - Claim on tax return
                    """)
        else:
            st.info("No donation data available for analytics")
    
    with tab4:
        # ====================================================================
        # MANAGE TAB
        # ====================================================================
        
        st.subheader("⚙️ Manage Donation Records")
        
        # Get all donations for management
        all_donations_manage = session.query(Donation).filter(
            and_(Donation.date >= start_date, Donation.date <= end_date)
        ).order_by(Donation.date.desc()).all()
        
        if all_donations_manage:
            st.info(f"Total: {len(all_donations_manage)} donation records")
            
            # Edit/Delete section
            st.markdown("#### ✏️ Edit or Delete Donation")
            
            donation_id = st.number_input("Enter Donation ID", min_value=1, step=1, key="donation_edit_id")
            
            if donation_id:
                donation = session.query(Donation).filter(Donation.id == donation_id).first()
                
                if donation:
                    st.success(f"Selected: {donation.charity} - {donation.date.strftime('%d %b %Y')} - {format_currency(donation.amount_paid)}")
                    
                    action = st.radio("Select Action", ["Edit", "Delete"], horizontal=True)
                    
                    if action == "Edit":
                        with st.form("edit_donation_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_date = st.date_input("Date", value=donation.date)
                                new_charity = st.text_input("Charity", value=donation.charity)
                                new_amount = st.number_input("Amount", value=float(donation.amount_paid), step=0.01)
                            
                            with col2:
                                new_gift_aid = st.checkbox("Gift Aid", value=donation.gift_aid)
                                new_notes = st.text_area("Notes", value=donation.notes or '')
                            
                            if st.form_submit_button("💾 Update Donation", type="primary"):
                                donation.date = new_date
                                donation.charity = new_charity
                                donation.amount_paid = new_amount
                                donation.gift_aid = new_gift_aid
                                donation.notes = new_notes
                                session.commit()
                                show_toast(f"Donation #{donation.id} updated", "success")
                                st.rerun()
                    
                    elif action == "Delete":
                        if confirm_delete(
                            f"donation_{donation.id}",
                            f"Donation #{donation.id}",
                            f"{donation.charity} — {format_currency(donation.amount_paid)} on {donation.date.strftime('%d %B %Y')}"
                        ):
                            session.delete(donation)
                            session.commit()
                            show_toast(f"Donation #{donation.id} deleted", "delete")
                            st.rerun()
                else:
                    st.error("❌ Donation not found")
            
            # Export functionality
            st.markdown("#### 📥 Export Donation Records")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Generate Gift Aid Report", use_container_width=True):
                    # Create DataFrame for export
                    data = []
                    total_gift_aid = 0
                    
                    for d in all_donations_manage:
                        if d.gift_aid:
                            charity_receives = d.amount_paid * 1.25
                            tax_relief_40 = d.amount_paid * 0.25
                            total_gift_aid += d.amount_paid
                        else:
                            charity_receives = d.amount_paid
                            tax_relief_40 = 0
                        
                        data.append({
                            'Date': d.date.strftime('%Y-%m-%d'),
                            'Charity': d.charity,
                            'Amount Paid': d.amount_paid,
                            'Gift Aid': 'Yes' if d.gift_aid else 'No',
                            'Charity Receives': charity_receives,
                            'Tax Relief (40%)': tax_relief_40,
                            'Notes': d.notes or ''
                        })
                    
                    df = pd.DataFrame(data)
                    
                    # Add summary row
                    summary = pd.DataFrame([{
                        'Date': 'TOTAL',
                        'Charity': '',
                        'Amount Paid': df['Amount Paid'].sum(),
                        'Gift Aid': '',
                        'Charity Receives': df['Charity Receives'].sum(),
                        'Tax Relief (40%)': df['Tax Relief (40%)'].sum(),
                        'Notes': f'Gift Aid donations: £{total_gift_aid:.2f}'
                    }])
                    
                    df = pd.concat([df, summary], ignore_index=True)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"gift_aid_report_{tax_year.replace('/', '-')}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📄 HMRC Summary", use_container_width=True):
                    total_gift_aid = sum(d.amount_paid for d in all_donations_manage if d.gift_aid)
                    
                    st.info(f"""
                    **Gift Aid Summary for HMRC**
                    
                    Tax Year: {tax_year}
                    
                    Total Gift Aid donations: **{format_currency(total_gift_aid)}**
                    
                    Enter this amount in Box 7 of your Self Assessment tax return.
                    
                    HMRC will automatically gross this up by 25% to calculate your tax relief.
                    
                    Tax relief available:
                    - 40% taxpayer: {format_currency(total_gift_aid * 0.25)}
                    - 45% taxpayer: {format_currency(total_gift_aid * 0.3125)}
                    """)
        else:
            st.info("No donation records found")
