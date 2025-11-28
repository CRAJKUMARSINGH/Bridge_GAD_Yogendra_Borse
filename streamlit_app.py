"""
Bridge GAD Generator - Streamlit Web UI
Professional interface for generating bridge drawings
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import sys
import os
from io import BytesIO
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from bridge_gad.bridge_generator import BridgeGADGenerator
from bridge_gad.advanced_features import (
    BridgeTemplates, DesignQualityChecker, 
    Bridge3DVisualizer, DesignComparator
)
from bridge_gad.multi_sheet_generator import DetailedSheetGenerator
from bridge_gad.ai_optimizer import AIDesignOptimizer, ReportGenerator, PerformancePredictor

# Page config
st.set_page_config(
    page_title="Bridge GAD Generator",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🌉 Bridge GAD Generator</h1>', unsafe_allow_html=True)
st.markdown("Generate Professional AutoCAD Bridge Drawings with RKS LEGAL Branding")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    acad_version = st.selectbox(
        "AutoCAD Version",
        ["R2010", "R2006"],
        help="Select AutoCAD format compatibility"
    )
    
    export_format = st.selectbox(
        "Export Format",
        ["dxf", "pdf", "png", "svg"],
        help="Select output file format"
    )
    
    st.divider()
    st.markdown("**📋 RKS LEGAL**")
    st.markdown("Techno Legal Consultants")
    st.markdown("📍 303 Vallabh Apartment")
    st.markdown("🤝 Professional Bridge Design")

# Main interface
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Generate", 
    "📋 Templates", 
    "✅ Quality Check",
    "🎨 3D Preview",
    "📊 Compare",
    "🤖 AI Optimizer",
    "ℹ️ Help"
])

# TAB 1: Generate Drawing
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Bridge Parameters")
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file with bridge parameters",
            type=["xlsx", "xls"],
            help="Excel file should contain VALUE, VARIABLE, DESCRIPTION columns"
        )
        
        if uploaded_file:
            st.success("✅ File uploaded successfully")
            
            # Show file preview
            with st.expander("👁️ Preview Data"):
                df = pd.read_excel(uploaded_file, header=None)
                st.dataframe(df.head(20), use_container_width=True)
        else:
            st.info("💡 Upload an Excel file to begin generating bridge drawings")
    
    with col2:
        st.subheader("Quick Stats")
        if uploaded_file:
            df = pd.read_excel(uploaded_file, header=None)
            df.columns = ['Value', 'Variable', 'Description']
            var_dict = df.set_index('Variable')['Value'].to_dict()
            
            st.metric("Spans", int(var_dict.get('NSPAN', 0)))
            st.metric("Span Length", f"{float(var_dict.get('SPAN1', 0)):.1f}m")
            st.metric("Width", f"{float(var_dict.get('CCBR', 0)):.2f}m")
    
    # Generate button
    if uploaded_file:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            generate_btn = st.button("🚀 Generate Drawing", use_container_width=True)
        
        with col2:
            batch_mode = st.checkbox("📦 Batch Mode (All Formats)")
        
        with col3:
            advanced = st.checkbox("⚙️ Advanced Options")
        
        if generate_btn:
            with st.spinner("🔄 Generating bridge drawing..."):
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        
                        # Save uploaded file
                        excel_path = temp_path / uploaded_file.name
                        with open(excel_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Generate drawing
                        gen = BridgeGADGenerator(acad_version=acad_version)
                        output_file = temp_path / f"bridge_gad.{export_format}"
                        
                        if gen.generate_complete_drawing(excel_path, output_file):
                            st.success("✅ Drawing generated successfully!")
                            
                            # Display file size
                            file_size = output_file.stat().st_size / 1024
                            st.info(f"📁 File size: {file_size:.1f} KB")
                            
                            # Download button
                            with open(output_file, "rb") as f:
                                st.download_button(
                                    label=f"⬇️ Download {export_format.upper()}",
                                    data=f.read(),
                                    file_name=f"bridge_drawing.{export_format}",
                                    mime=f"application/{export_format}"
                                )
                            
                            # Batch download all formats
                            if batch_mode:
                                st.subheader("📦 Batch Downloads")
                                formats = ["dxf", "pdf", "png", "svg"]
                                
                                for fmt in formats:
                                    try:
                                        out = temp_path / f"bridge_gad_batch.{fmt}"
                                        gen.generate_complete_drawing(excel_path, out)
                                        with open(out, "rb") as f:
                                            st.download_button(
                                                f"⬇️ {fmt.upper()}",
                                                data=f.read(),
                                                file_name=f"bridge_drawing.{fmt}"
                                            )
                                    except:
                                        pass
                        else:
                            st.error("❌ Failed to generate drawing")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Multi-Sheet Detailed Drawings
        st.divider()
        st.subheader("📋 Detailed Multi-Sheet Drawings (4 Sheets)")
        st.markdown("Generate all 4 detailed views on separate A4 landscape sheets")
        
        if uploaded_file:
            if st.button("🎨 Generate 4-Sheet Detailed Package", use_container_width=True):
                with st.spinner("📐 Generating detailed sheets (Pier, Abutment, Plan, Section)..."):
                    try:
                        with tempfile.TemporaryDirectory() as temp_dir:
                            temp_path = Path(temp_dir)
                            
                            # Save uploaded file
                            excel_path = temp_path / uploaded_file.name
                            with open(excel_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Read Excel to get variables
                            df = pd.read_excel(excel_path, header=None)
                            df.columns = ['Value', 'Variable', 'Description']
                            variables = df.set_index('Variable')['Value'].to_dict()
                            
                            # Generate multi-sheet drawings
                            sheet_gen = DetailedSheetGenerator(acad_version=acad_version)
                            output_file = temp_path / "bridge_detailed.dxf"
                            
                            if sheet_gen.generate_all_sheets(variables, output_file):
                                st.success("✅ All 4 sheets generated successfully!")
                                st.info("📌 Generated Sheets:\n1. Pier Elevation (Enlarged)\n2. Abutment Elevation (Enlarged)\n3. Plan View (Top)\n4. Section View (Profile)")
                                
                                # Download individual sheets
                                st.subheader("📥 Download Sheets")
                                col1, col2 = st.columns(2)
                                
                                sheet_names = ["Pier_Elevation", "Abutment_Elevation", "Plan_View", "Section_View"]
                                
                                for i, sheet_name in enumerate(sheet_names, 1):
                                    sheet_file = temp_path / f"bridge_detailed_Sheet{i}.dxf"
                                    if sheet_file.exists():
                                        with open(sheet_file, "rb") as f:
                                            col = col1 if i % 2 == 1 else col2
                                            with col:
                                                st.download_button(
                                                    f"📥 Sheet {i}: {sheet_name}",
                                                    data=f.read(),
                                                    file_name=f"Bridge_{sheet_name}.dxf"
                                                )
                            else:
                                st.error("❌ Failed to generate detailed sheets")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# TAB 2: Templates
with tab2:
    st.subheader("🎯 Quick-Start Templates")
    st.markdown("Select a standard bridge template to get started instantly:")
    
    templates = BridgeTemplates.list_templates()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_template = st.selectbox(
            "Choose Template",
            list(templates.keys()),
            format_func=lambda x: templates[x]
        )
    
    if selected_template:
        template = BridgeTemplates.get_template(selected_template)
        
        with col2:
            st.metric("Bridge Type", template.bridge_type)
        
        st.markdown(f"**Description**: {template.description}")
        
        # Show template parameters
        st.dataframe(pd.DataFrame([template.parameters]).T, use_container_width=True)
        
        # Export template
        template_df = pd.DataFrame([
            [value, key, key] for key, value in template.parameters.items()
        ], columns=['Value', 'Variable', 'Description'])
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Parameters')
        excel_buffer.seek(0)
        
        st.download_button(
            f"📥 Use {template.name}",
            data=excel_buffer.getvalue(),
            file_name=f"{selected_template}_bridge.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# TAB 3: Quality Check
with tab3:
    st.subheader("✅ Design Quality & Standards Compliance")
    st.markdown("Validate your bridge design against IRC & IS codes")
    
    quality_file = st.file_uploader(
        "Upload Excel for quality check",
        type=["xlsx", "xls"],
        key="quality_check"
    )
    
    if quality_file:
        try:
            df = pd.read_excel(quality_file, header=None)
            df.columns = ['Value', 'Variable', 'Description']
            variables = df.set_index('Variable')['Value'].to_dict()
            
            checker = DesignQualityChecker(variables)
            results = checker.validate()
            
            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status = "✅ PASS" if results['is_valid'] else "❌ ISSUES FOUND"
                st.metric("Status", status)
            
            with col2:
                st.metric("Compliance Score", f"{results['compliance_score']}/100")
            
            with col3:
                st.metric("Issues", len(results['critical_issues']))
            
            # Display issues
            if results['critical_issues']:
                st.error("🔴 Critical Issues:")
                for issue in results['critical_issues']:
                    st.write(f"  • {issue}")
            
            if results['warnings']:
                st.warning("🟡 Warnings:")
                for warning in results['warnings']:
                    st.write(f"  • {warning}")
            
            if results['is_valid']:
                st.success("✅ Design complies with all standards!")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# TAB 4: 3D Preview
with tab4:
    st.subheader("🎨 3D Bridge Visualization")
    
    viz_file = st.file_uploader(
        "Upload Excel for 3D preview",
        type=["xlsx", "xls"],
        key="3d_preview"
    )
    
    if viz_file:
        try:
            df = pd.read_excel(viz_file, header=None)
            df.columns = ['Value', 'Variable', 'Description']
            variables = df.set_index('Variable')['Value'].to_dict()
            
            visualizer = Bridge3DVisualizer(variables)
            stats = visualizer.get_summary_stats()
            
            if stats:
                st.info("📐 3D Bridge Dimensions:")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Length", f"{stats['x_range'][1]:.1f}m")
                with col2:
                    st.metric("Width", f"{stats['y_range'][1]:.1f}m")
                with col3:
                    st.metric("Approximate Volume", f"{stats['volume_approximate']:.1f}m³")
                
                # 3D matplotlib visualization
                try:
                    import matplotlib.pyplot as plt
                    from mpl_toolkits.mplot3d import Axes3D
                    
                    mesh = visualizer.generate_3d_mesh()
                    if mesh.get('vertices') is not None:
                        fig = plt.figure(figsize=(10, 6))
                        ax = fig.add_subplot(111, projection='3d')
                        
                        vertices = mesh['vertices']
                        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], s=10)
                        
                        ax.set_xlabel('Length (m)')
                        ax.set_ylabel('Width (m)')
                        ax.set_zlabel('Height (m)')
                        ax.set_title('Bridge 3D Model Preview')
                        
                        st.pyplot(fig)
                except:
                    st.info("3D visualization loading...")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# TAB 5: Design Comparison
with tab5:
    st.subheader("📊 Compare Two Designs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Design 1**")
        file1 = st.file_uploader("Upload Design 1", type=["xlsx", "xls"], key="design1")
    
    with col2:
        st.markdown("**Design 2**")
        file2 = st.file_uploader("Upload Design 2", type=["xlsx", "xls"], key="design2")
    
    if file1 and file2:
        try:
            df1 = pd.read_excel(file1, header=None)
            df1.columns = ['Value', 'Variable', 'Description']
            vars1 = df1.set_index('Variable')['Value'].to_dict()
            
            df2 = pd.read_excel(file2, header=None)
            df2.columns = ['Value', 'Variable', 'Description']
            vars2 = df2.set_index('Variable')['Value'].to_dict()
            
            comparator = DesignComparator(vars1, vars2)
            comparison = comparator.compare()
            
            # Display comparison
            comparison_df = pd.DataFrame({
                'Parameter': comparison.keys(),
                'Design 1': [str(v['design1']) for v in comparison.values()],
                'Design 2': [str(v['design2']) for v in comparison.values()],
                'Change': [f"{v.get('percent_change', 'N/A')}" for v in comparison.values()]
            })
            
            st.dataframe(comparison_df, use_container_width=True)
            
            st.info(comparator.get_summary())
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# TAB 6: Help (renamed from tab3)
    st.subheader("📋 Sample Excel Template")
    st.markdown("""
    Create an Excel file with these columns:
    | Column | Purpose |
    |--------|---------|
    | Value | Parameter value |
    | Variable | Parameter name |
    | Description | What this parameter means |
    """)
    
    # Create sample data
    sample_data = {
        'Value': [186, 100, 0, 100, 0, 50, 10, 1, 115, 3, 12, 0, 110.98, 100, 1.2, 12, 100, 1.0, 4.5, 12, 0.75, 11.1, 0.23, 0.15, 110, 109.4, 0.38, 0.08, 36, 110, 'Highway Bridge Project', 'RKS LEGAL', 'Techno Legal Consultants', '303 Vallabh Apartment, Navratna Complex, Bhuwana, Udaipur', 'crajkumarsingh@hotmail.com', '+919414163019', 'BR-2025-001'],
        'Variable': ['SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'LEFT', 'RIGHT', 'XINCR', 'YINCR', 'TOPRL', 'NSPAN', 'SPAN1', 'ABTL', 'RTL', 'FUTRL', 'PIERTW', 'PIERST', 'FUTRL', 'FUTD', 'FUTW', 'FUTL', 'SLBTHE', 'CCBR', 'KERBW', 'KERBD', 'CAPT', 'CAPB', 'APTHK', 'WCTH', 'LBRIDGE', 'SOFL', 'PROJECT_NAME', 'COMPANY_NAME', 'COMPANY_FULL', 'ADDRESS', 'EMAIL', 'MOBILE', 'PROJECT_CODE'],
        'Description': ['Horizontal Scale', 'Vertical Scale', 'Skew Angle', 'Datum Level', 'Left Position', 'Right Position', 'X Increment', 'Y Increment', 'Top RL', 'Number of Spans', 'Span Length', 'Abutment L', 'Rail Top Level', 'Foundation RL', 'Pier Width', 'Pier Length', 'Foundation RL', 'Foundation Depth', 'Foundation Width', 'Foundation Length', 'Slab Thickness', 'Carriageway Width', 'Kerb Width', 'Kerb Depth', 'Cap Top', 'Cap Bottom', 'Approach Thickness', 'Wearing Course', 'Bridge Length', 'Soffit Level', 'Project Name', 'Company Name', 'Full Company Name', 'Office Address', 'Contact Email', 'Contact Mobile', 'Project Code']
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, use_container_width=True, height=400)
    
    # Download template
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        sample_df.to_excel(writer, index=False, sheet_name='Parameters')
    excel_buffer.seek(0)
    
    st.download_button(
        label="📥 Download Template Excel",
        data=excel_buffer.getvalue(),
        file_name="bridge_gad_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# TAB 6: Help
with tab6:
    st.subheader("❓ Frequently Asked Questions")
    
    with st.expander("What formats are supported?"):
        st.markdown("""
        - **DXF**: AutoCAD format (2006 & 2010 compatible)
        - **PDF**: Professional PDF with layouts
        - **PNG**: High-quality raster image
        - **SVG**: Scalable vector graphics
        """)
    
    with st.expander("How do I customize the title block?"):
        st.markdown("""
        Add these parameters to your Excel file:
        - `PROJECT_NAME`: Your project title
        - `COMPANY_NAME`: Company abbreviation (RKS LEGAL)
        - `COMPANY_FULL`: Full company name
        - `ADDRESS`: Office address
        - `EMAIL`: Contact email
        - `MOBILE`: Contact phone
        - `PROJECT_CODE`: Project reference number
        """)
    
    with st.expander("What are the bridge parameters?"):
        st.markdown("""
        **Geometry Parameters:**
        - NSPAN: Number of spans
        - SPAN1: Span length (meters)
        - CCBR: Carriageway width
        
        **Levels:**
        - DATUM: Datum level
        - RTL: Rail top level
        - SOFL: Soffit level
        
        **Components:**
        - PIERTW: Pier thickness
        - FUTW: Footing width
        - SLBTHE: Slab thickness
        """)
    
    with st.expander("🌉 About RKS LEGAL"):
        st.markdown("""
        **RKS LEGAL - Techno Legal Consultants**
        
        📍 303 Vallabh Apartment, Navratna Complex, Bhuwana
        Udaipur -313001
        
        📧 Email: crajkumarsingh@hotmail.com
        📱 Mobile: +919414163019
        
        Professional bridge design and engineering consultancy
        """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8rem;">
    🌉 Bridge GAD Generator v2.0 | AutoCAD 2006+ Compatible | Vercel Ready
    <br>
    Powered by FastAPI + Streamlit | RKS LEGAL Branding
</div>
""", unsafe_allow_html=True)

# TAB 6: AI Optimizer ⭐ NEW ADVANCED FEATURE
with tab6:
    st.subheader("🤖 AI Design Optimizer & Cost Estimator")
    st.markdown("Intelligent optimization with cost analysis, material estimates, and performance predictions - NO external API needed")
    
    ai_file = st.file_uploader(
        "Upload Excel for AI optimization",
        type=["xlsx", "xls"],
        key="ai_optimizer"
    )
    
    if ai_file:
        try:
            from bridge_gad.ai_optimizer import AIDesignOptimizer, ReportGenerator, PerformancePredictor
            
            df = pd.read_excel(ai_file, header=None)
            df.columns = ['Value', 'Variable', 'Description']
            variables = df.set_index('Variable')['Value'].to_dict()
            
            optimizer = AIDesignOptimizer(variables)
            analysis = optimizer.analyze_design()
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Efficiency Score", f"{analysis['efficiency_score']}%")
            with col2:
                st.metric("Cost Savings", f"{analysis['cost_potential']}%")
            with col3:
                st.metric("Time Save", f"{analysis['time_savings']}m")
            with col4:
                st.metric("Waste", f"{analysis['material_waste']}%")
            with col5:
                st.metric("Safety", f"{analysis['safety_margin']}%")
            
            st.divider()
            optimization = optimizer.optimize()
            
            st.subheader("📊 Optimization Results")
            st.success(f"💡 Potential Savings: ₹{int(optimization.savings.get('cost_inr', 0)):,}")
            st.info(f"📍 Estimated Cost: ₹{int(optimization.cost_estimate):,}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Concrete", f"{optimization.material_quantities.get('concrete_m3', 0):.1f}m³")
            with col2:
                st.metric("Steel", f"{optimization.material_quantities.get('steel_tonnes', 0):.1f}t")
            with col3:
                st.metric("Formwork", f"{optimization.material_quantities.get('formwork_m2', 0):.0f}m²")
            with col4:
                st.metric("Labour", f"{optimization.material_quantities.get('labour_days', 0):.0f}d")
            
            st.divider()
            st.subheader("🎯 Recommendations")
            for i, rec in enumerate(optimization.recommendations, 1):
                st.write(f"**{i}.** {rec}")
            
            if st.button("📄 Download Report"):
                report_gen = ReportGenerator(variables, optimization)
                report_text = report_gen.generate_summary()
                st.download_button("⬇️ Download", data=report_text, file_name=f"optimization_report.txt")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# TAB 7: Help
with tab7:
