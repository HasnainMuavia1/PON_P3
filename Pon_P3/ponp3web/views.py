import io
import csv
import pandas as pd
from django.shortcuts import render, HttpResponse, redirect
from .models import data, Counter, Genomic, Transcript
from django.core.mail import EmailMessage
from django.db import transaction
from .genomic_conversion import convert_genomics_to_variations  # Import the conversion functions
from .transcript_conversion import convert_transcripts_to_variations  # Import the conversion functions
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
import os


# from .testpdf import dataframe_to_pdf


def index(request):
    return render(request, 'index.html')


def dataframe_to_pdf(dataframe, pdf_filename, email, task_number):
    # Determine the base directory
    if 'BASE_DIR' in dir(settings):
        base_dir = settings.BASE_DIR
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Create paths
    pdf_path = os.path.join(base_dir, 'output', pdf_filename)
    logo_path = os.path.join(base_dir, 'ponp3web', 'static', 'img', 'logo_final.png')

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Create a PDF document
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)

    # Elements for the PDF
    elements = []

    # Load and resize logo image
    logo = Image(logo_path)
    logo.drawHeight = 1.2 * inch
    logo.drawWidth = 1.2 * inch

    # Add text beside the logo
    styles = getSampleStyleSheet()
    title = Paragraph("<b>Prediction Results</b>", styles['Title'])  # Title text

    # Create a table for the header with the logo and title side by side
    header_data = [[logo, title]]
    header_table = Table(header_data, colWidths=[1.5 * inch, 6 * inch])  # Adjusted column widths to take full width
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE')
    ]))

    # Add the header (logo + title) to the elements
    elements.append(header_table)
    elements.append(Spacer(1, 24))

    # Add extra table for Email and Task Number (full width)
    extra_data = [['Email', 'Task Number'], [email, task_number]]  # Data for the new table
    extra_table = Table(extra_data, colWidths=[4.08 * inch, 4.08 * inch])  # Split equally to fill full width

    # Style the extra table
    extra_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.brown),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ])
    extra_table.setStyle(extra_table_style)

    # Add the extra table to the elements
    elements.append(extra_table)
    elements.append(Spacer(1, 24))

    # Convert DataFrame to list format for the Table
    data = [list(dataframe.columns)] + dataframe.values.tolist()

    # Calculate column widths dynamically to take full width
    # num_columns = len(dataframe.columns)
    # col_widths = [6.5 * inch / num_columns] * num_columns  # Adjust the width based on available page space

    # Create a table with the data (full width)
    table = Table(data)

    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.brown),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ])
    table.setStyle(style)

    # Add the data table to the elements
    elements.append(table)

    # Add footer text at the bottom right
    footer_text = Paragraph(
        "<b>Protein Structure and Bioinformatics Group</b><br/><b>Biomedical Center (BMC), Lund University, Sweden</b>",
        styles['Normal']
    )

    # Add enough Spacer to push the footer to the bottom right
    elements.append(Spacer(1, 50))  # Adjust this value based on the page size and table height
    elements.append(footer_text)

    # Build the PDF
    pdf.build(elements)

    print(f"PDF saved at: {pdf_path}")


# def dataframe_to_pdf(dataframe, pdf_filename):
#     # Determine the base directory
#     if 'BASE_DIR' in dir(settings):
#         # If running in Django
#         base_dir = settings.BASE_DIR
#     else:
#         # If running outside Django (e.g., in PyCharm)
#         base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
#     # Create paths
#     pdf_path = os.path.join(base_dir, 'output', pdf_filename)
#     logo_path = os.path.join(base_dir, 'ponp3web', 'static', 'img', 'logo_final.png')
#
#     # Ensure the output directory exists
#     os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
#
#     # Create a PDF document
#     pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
#
#     # Elements for the PDF
#     elements = []
#
#     # Load and resize logo image
#     logo = Image(logo_path)
#     logo.drawHeight = 1.2 * inch
#     logo.drawWidth = 1.2 * inch
#
#     # Add text beside the logo
#     styles = getSampleStyleSheet()
#     title = Paragraph("<b>Prediction Results</b>", styles['Title'])  # Title text
#
#     # Create a table for the header with the logo and title side by side
#     header_data = [[logo, title]]
#     header_table = Table(header_data, colWidths=[1.5 * inch, 4.5 * inch])  # Adjust the column widths
#     header_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Align logo to the left
#         ('VALIGN', (0, 0), (1, 0), 'MIDDLE')  # Vertically align the logo and text to the middle
#     ]))
#
#     # Add the header (logo + title) to the elements
#     elements.append(header_table)
#     elements.append(Spacer(1, 24))  # Add some space after the header
#
#     # Convert DataFrame to list format for the Table
#     data = [list(dataframe.columns)] + dataframe.values.tolist()
#
#     # Create a table with the data
#     table = Table(data)
#
#     # Style the table
#     style = TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.brown),  # Header background color
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add borders to table
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold header
#         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Normal font for body
#         ('FONTSIZE', (0, 0), (-1, 0), 10),  # Header font size
#         ('FONTSIZE', (0, 1), (-1, -1), 8),  # Body font size
#         ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),  # Body background color
#     ])
#     table.setStyle(style)
#
#     # Add the data table to the elements
#     elements.append(table)
#
#     # Add footer text at the bottom right
#     footer_text = Paragraph(
#         "<b>Protein Structure and Bioinformatics Group</b><br/><b>Biomedical Center (BMC), Lund University, Sweden</b>",
#         styles['Normal']
#     )
#
#     # Add enough Spacer to push the footer to the bottom right
#     elements.append(Spacer(1, 50))  # Adjust this value based on the page size and table height
#     elements.append(footer_text)
#
#     # Build the PDF
#     pdf.build(elements)
#
#     print(f"PDF saved at: {pdf_path}")


# Function to handle user input and process data
def input(request):
    if request.method == 'POST':
        counter, created = Counter.objects.get_or_create(pk=1)  # Assuming a single counter instance
        counter.increment()
        text = request.POST.get('te')
        file = request.FILES.get('csv_data')
        email = request.POST['e']

        if not text:
            # if the file is excel file then convert into csv
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                file = pd.read_excel(file)
                # csv_file = file.to_csv(index=False)
            result = handle_uploaded_file2(file, email, counter)
            if result == 'Error':
                return render(request, 'input_Prediction.html',
                              {'msg': 'Wrong format or one of the keys is missing', 'counter': Counter.objects.first()})
            else:
                return render(request, 'input_Prediction.html',
                              {'msg': 'Email sent successfully! Check your email', 'counter': Counter.objects.first()})
        elif not file:
            result = get_values_combine(text, email, counter)
            if result == 'Error':
                return render(request, 'input_Prediction.html',
                              {'msg': 'Failed to send email', 'counter': Counter.objects.first()})
            else:
                return render(request, 'input_Prediction.html',
                              {'msg': 'Email sent successfully! Check your email', 'counter': Counter.objects.first()})

    return render(request, 'input_Prediction.html', {'counter': Counter.objects.first()})


# Function to check if the genomic variation is already present in the database
def check_genomic_in_db(genomic_variation_list):
    existing_genomics = Genomic.objects.filter(genomic_variation__in=genomic_variation_list)
    return existing_genomics


# Function to save genomic variations, refseq, and variation values in the database
def save_genomic_in_db(genomic_variation, refseq_ids, variation_ids):
    if refseq_ids and variation_ids:
        genomic = Genomic(
            genomic_variation=genomic_variation,
            refseq_ids=refseq_ids,
            variation_ids=variation_ids
        )
        genomic.save()


def input_genomic(request):
    """
    View to handle input of genomic variations and convert them to protein variations.
    """
    if request.method == 'POST':
        counter, created = Counter.objects.get_or_create(pk=1)  # Assuming a single counter instance
        counter.increment()
        file = request.FILES.get('csv_data')  # Get uploaded file
        genomic_variations = request.POST.get('te')  # Get text input for genomic variations
        email = request.POST.get('e')  # Get the email input

        genomic_variation_list = []

        # Check if the text input is empty
        if not genomic_variations:
            if file:
                # Ensure the file is an Excel or CSV file
                if file.name.endswith(('.xlsx', '.xls')):
                    try:
                        file = pd.read_excel(file, header=None)
                        genomic_variation_list = file.iloc[:, 0].tolist()  # Convert the Excel file to a list
                    except Exception as e:
                        return render(request, 'input_genomic_variation.html',
                                      {'msg': 'Error reading Excel file: ' + str(e)})
                elif file.name.endswith('.csv'):
                    try:
                        file = pd.read_csv(file, header=None)
                        genomic_variation_list = file.iloc[:, 0].tolist()  # Convert the CSV file to a list
                    except Exception as e:
                        return render(request, 'input_genomic_variation.html',
                                      {'msg': 'Error reading CSV file: ' + str(e), 'counter': Counter.objects.first()})
                else:
                    return render(request, 'input_genomic_variation.html',
                                  {'msg': 'Invalid file format. Please upload a .xlsx, .xls, or .csv file.',
                                   'counter': Counter.objects.first()})
            else:
                return render(request, 'input_genomic_variation.html',
                              {'msg': 'No file or genomic variations provided.', 'counter': Counter.objects.first()})
        else:
            # If text input is provided, split it into a list
            genomic_variation_list = genomic_variations.splitlines()

        # Check if genomic variations exist in the database
        existing_genomics = check_genomic_in_db(genomic_variation_list)
        existing_variations = list(existing_genomics.values('genomic_variation', 'refseq_ids', 'variation_ids'))

        # Separate the genomic variations that are not present in the database
        genomics_to_convert = [g for g in genomic_variation_list if
                               g not in existing_genomics.values_list('genomic_variation', flat=True)]

        conversion_results = []
        if genomics_to_convert:
            try:
                print("Converting new genomic variations!")
                # Process the new genomic variations
                conversion_results = convert_genomics_to_variations(genomics_to_convert)

                # Save new genomic variations in the database
                for result in conversion_results:
                    save_genomic_in_db(
                        genomic_variation=result['genomic_variation'],
                        refseq_ids=result['refseq_ids'],
                        variation_ids=result['variation_ids']
                    )

            except Exception as e:
                return render(request, 'input_genomic_variation.html',
                              {'msg': 'Error during conversion: ' + str(e), 'counter': Counter.objects.first()})

        # Combine existing variations and newly converted variations
        if existing_variations:
            all_results = existing_variations + conversion_results
        else:
            all_results = conversion_results

        # Create a DataFrame from the combined results
        results_df = pd.DataFrame(all_results)

        # Handle file and email sending
        result = handle_uploaded_file2(results_df, email, counter)
        if result == 'Error':
            return render(request, 'input_genomic_variation.html',
                          {'msg': 'Failed to send email. Please try again.', 'counter': Counter.objects.first()})
        else:
            return render(request, 'input_genomic_variation.html',
                          {'msg': 'Email sent successfully! Check your inbox.', 'counter': Counter.objects.first()})

    return render(request, 'input_genomic_variation.html', {'counter': Counter.objects.first()})


# Function to check if the transcript variation is already present in the database
def check_transcript_in_db(transcript_variation_list):
    existing_transcripts = Transcript.objects.filter(transcript_variation__in=transcript_variation_list)
    return existing_transcripts


# Function to save transcript variations, refseq, and variation values in the database
def save_transcript_in_db(transcript_variation, refseq_ids, variation_ids):
    if refseq_ids and variation_ids:
        transcript = Transcript(
            transcript_variation=transcript_variation,
            refseq_ids=refseq_ids,
            variation_ids=variation_ids
        )
        transcript.save()


def input_transcript(request):
    """
    View to handle input of transcript variations and convert them to protein variations.
    """
    if request.method == 'POST':
        counter, created = Counter.objects.get_or_create(pk=1)  # Assuming a single counter instance
        counter.increment()
        file = request.FILES.get('csv_data')  # Get uploaded file
        transcript_variations = request.POST.get('te')  # Get text input for transcript variations
        email = request.POST.get('e')  # Get the email input

        transcript_variation_list = []

        # Check if the text input is empty
        if not transcript_variations:
            if file:
                # Ensure the file is an Excel or CSV file
                if file.name.endswith(('.xlsx', '.xls')):
                    try:
                        file = pd.read_excel(file, header=None)
                        transcript_variation_list = file.iloc[:, 0].tolist()  # Convert the Excel file to a list
                    except Exception as e:
                        return render(request, 'input_transcript_variation.html',
                                      {'msg': 'Error reading Excel file: ' + str(e)})
                elif file.name.endswith('.csv'):
                    try:
                        file = pd.read_csv(file, header=None)
                        transcript_variation_list = file.iloc[:, 0].tolist()  # Convert the CSV file to a list
                    except Exception as e:
                        return render(request, 'input_transcript_variation.html',
                                      {'msg': 'Error reading CSV file: ' + str(e), 'counter': Counter.objects.first()})
                else:
                    return render(request, 'input_transcript_variation.html',
                                  {'msg': 'Invalid file format. Please upload a .xlsx, .xls, or .csv file.',
                                   'counter': Counter.objects.first()})
            else:
                return render(request, 'input_transcript_variation.html',
                              {'msg': 'No file or transcript variations provided.', 'counter': Counter.objects.first()})
        else:
            # If text input is provided, split it into a list
            transcript_variation_list = transcript_variations.splitlines()

        # Check if transcript variations exist in the database
        existing_transcripts = check_transcript_in_db(transcript_variation_list)
        existing_variations = list(existing_transcripts.values('transcript_variation', 'refseq_ids', 'variation_ids'))

        # Separate the transcripts that are not present in the database
        transcripts_to_convert = [t for t in transcript_variation_list if
                                  t not in existing_transcripts.values_list('transcript_variation', flat=True)]

        conversion_results = []
        if transcripts_to_convert:
            try:
                print("Converting new transcript variations!")
                # Process the new transcripts
                conversion_results = convert_transcripts_to_variations(transcripts_to_convert)

                # Save new transcript variations in the database
                for result in conversion_results:
                    save_transcript_in_db(
                        transcript_variation=result['transcript_variation'],
                        refseq_ids=result['refseq_ids'],
                        variation_ids=result['variation_ids']
                    )

            except Exception as e:
                return render(request, 'input_transcript_variation.html',
                              {'msg': 'Error during conversion: ' + str(e), 'counter': Counter.objects.first()})

        # Check if existing variations are not empty before appending
        if existing_variations:
            all_results = existing_variations + conversion_results
        else:
            all_results = conversion_results

        # Create a DataFrame from the combined results
        results_df = pd.DataFrame(all_results)

        # Handle file and email sending
        result = handle_uploaded_file2(results_df, email, counter)
        if result == 'Error':
            return render(request, 'input_transcript_variation.html',
                          {'msg': 'Failed to send email. Please try again.', 'counter': Counter.objects.first()})
        else:
            return render(request, 'input_transcript_variation.html',
                          {'msg': 'Email sent successfully! Check your inbox.', 'counter': Counter.objects.first()})

    return render(request, 'input_transcript_variation.html', {'counter': Counter.objects.first()})


def handle_uploaded_file2(df, email, counter):
    """
    Process the uploaded CSV file and create a combined CSV file based on filtered data.
    This version works with any number of columns, only filtering using 'refseq_ids' and 'variation_ids',
    and keeps all other columns intact.
    """
    base_dir = settings.BASE_DIR
    path = base_dir / 'output'
    print(df.head())
    required_keys = {'refseq_ids', 'variation_ids'}

    # Ensure the required keys ('refseq_ids' and 'variation_ids') exist in the DataFrame
    if required_keys.issubset(df.columns):
        print("Valid input, proceeding with processing...")

        # Check if all values in 'refseq_ids' and 'variation_ids' are None
        all_none = df['refseq_ids'].isna().all() and df['variation_ids'].isna().all()

        if all_none:
            # Initialize the new columns with None or appropriate default values
            df['meanProb'] = None
            df['stdProb'] = None
            df['pred_label'] = None
            df['comments'] = "There is no record for this variation in database"
            dataframe_to_pdf(df, "prediction_results.pdf", email, counter)
            # Save the final DataFrame to a CSV buffer
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            # Send the final CSV file via email
            email_message = EmailMessage(
                'Predictions for your uploaded file are ready.',
                'Upon the usage the users are requested to use the following citation(s):\n Thank you for using our webserver \n Protein Structure and Bioinformatics Group - Lund University.',
                to=[email]
            )
            email_message.attach('Prediction_results.txt', csv_buffer.getvalue(), 'text/csv')
            email_message.attach_file(f"{path}/prediction_results.pdf")
            email_message.send()
            remove_path = base_dir / "output" / "prediction_results.pdf"
            os.remove(remove_path)

            return 'success'

        # If not all are None, proceed with the database operations
        # Group by 'refseq_ids'
        grouped = df.groupby('refseq_ids')
        combined_data = []

        for var1, group in grouped:
            var2_list = group['variation_ids'].tolist()
            var2_list = [k.upper() for k in var2_list]

            # Query the database using 'refseq_ids' and 'variation_ids'
            if var2_list:
                results = data.objects.filter(refseq_ids=var1, variation_ids__in=var2_list)
            else:
                results = data.objects.filter(refseq_ids=var1)

            # Convert the results to a list of dictionaries
            data_list = list(
                results.values('refseq_ids', 'variation_ids', 'meanProb', 'stdProb', 'pred_label', 'comments'))

            combined_data.extend(data_list)

        # Create a DataFrame from the combined data
        combined_df = pd.DataFrame(combined_data)

        # Check if combined_df is empty
        if combined_df.empty:
            # No results found, fill the DataFrame with None values and send email
            df['meanProb'] = None
            df['stdProb'] = None
            df['pred_label'] = None
            df['comments'] = "There is no record for this variation in database"

            dataframe_to_pdf(df, "prediction_results.pdf", email, counter)
            # Save the final DataFrame to a CSV buffer
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            # Send the final CSV file via email
            email_message = EmailMessage(
                'Predictions for your uploaded file are ready.',
                'Upon the usage the users are requested to use the following citation(s):\n Thank you for using our webserver \n Protein Structure and Bioinformatics Group - Lund University.',
                to=[email]
            )

            email_message.attach('Prediction_results.txt', csv_buffer.getvalue(), 'text/csv')
            email_message.attach_file(f"{path}/prediction_results.pdf")
            email_message.send()
            # then remove file
            remove_path = base_dir / "output" / "prediction_results.pdf"
            os.remove(remove_path)
            return 'success'

        # Drop duplicates in the combined DataFrame based on 'refseq_ids' and 'variation_ids'
        combined_df.drop_duplicates(subset=['refseq_ids', 'variation_ids'], inplace=True)

        # Merge the combined data with the original DataFrame (keeping all other columns intact)
        final_df = pd.merge(df, combined_df, on=['refseq_ids', 'variation_ids'], how='left')

        final_df['comments'].fillna("There is no data for this variation", inplace=True)

        print("final_df_columns", final_df.columns)
        print(final_df.tail())
        # Call the function

        dataframe_to_pdf(final_df, "prediction_results.pdf", email, counter)

        # Save the final DataFrame to a CSV buffer
        csv_buffer = io.StringIO()
        final_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Send the final CSV file via email
        email_message = EmailMessage(
            'Predictions for your uploaded file are ready.',
            'Upon the usage the users are requested to use the following citation(s):\n Thank you for using our webserver \n Protein Structure and Bioinformatics Group - Lund University.',
            to=[email]
        )
        email_message.attach('Prediction_results.txt', csv_buffer.getvalue(), 'text/csv')
        email_message.attach_file(f"{path}/prediction_results.pdf")

        email_message.send()
        remove_path = base_dir / "output" / "prediction_results.pdf"
        os.remove(remove_path)
        return 'success'

    else:
        return 'Error: Required columns (refseq_ids, variation_ids) are missing.'


def get_values_combine(text, email, counter):
    blocks = text.split('>')
    combined_data = []
    missing_data = []  # List to store missing data (for cases where no match is found)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        if lines:
            refseq_id = lines[0].strip()
            variation_ids = [item.strip().upper() for item in lines[1:] if item.strip()]

            # If variation_ids is empty, skip processing
            if not variation_ids:
                continue

            # Query for matching data
            results = data.objects.filter(refseq_ids=refseq_id, variation_ids__in=variation_ids)
            data_list = list(results.values('refseq_ids', 'variation_ids', 'meanProb', 'stdProb', 'pred_label','comments'))

            if data_list:
                combined_data.extend(data_list)
            else:
                # If no data found, store the refseq and variation ids with None values
                for variation_id in variation_ids:
                    missing_data.append({
                        'refseq_ids': refseq_id,
                        'variation_ids': variation_id,
                        'meanProb': None,
                        'stdProb': None,
                        'pred_label': None,
                        'comments': "There is no record for the input Variation"
                    })

    # Create the DataFrame with both found data and missing data
    combined_data.extend(missing_data)
    combined_df = pd.DataFrame(combined_data)

    # Drop duplicates based on 'refseq_ids' and 'variation_ids'
    combined_df.drop_duplicates(subset=['refseq_ids', 'variation_ids'], inplace=True)

    # Convert DataFrame to CSV format
    csv_buffer = io.StringIO()
    combined_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Send email with results
    try:
        email_message = EmailMessage(
            'Predictions for your uploaded file are ready.',
            'Upon the usage, the users are requested to use the following citation(s):\n Thank you for using our webserver.\n Protein Structure and Bioinformatics Group - Lund University.',
            to=[email]
        )

        # Attach the CSV data
        email_message.attach('prediction_results.txt', csv_buffer.getvalue(), 'text/csv')

        # Generate PDF and attach
        base_dir = settings.BASE_DIR
        path = os.path.join(base_dir, 'output')
        dataframe_to_pdf(combined_df, "prediction_results.pdf", email, counter)
        email_message.attach_file(f"{path}/prediction_results.pdf")

        # Remove the PDF after sending
        os.remove(f'{path}/prediction_results.pdf')

        # Send the email
        email_message.send()

    except Exception as e:
        print(f"Error sending email: {e}")
        return 'Error'


def upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for f in files:
            process_csv(f)
        return render(request, 'upload.html', {'msg': "Upload Successfully !"})

    return render(request, 'upload.html')


def process_csv(csv_file, batch_size=10000):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # List to hold all the objects to be created
    objects_to_create = []

    # Iterate over the rows of the DataFrame and prepare to save to the database
    for _, row in df.iterrows():
        # Append each row's data without checking for duplicates
        if 'Comment' in df.columns:
            objects_to_create.append(data(
                refseq_ids=row['refseq_ids'],
                variation_ids=row['variation_ids'],
                meanProb=row['meanProb'],
                stdProb=row['standardDev'],
                pred_label=row['Pred_label'],
                comments=row['Comment']
            ))
        else:
            objects_to_create.append(data(
                refseq_ids=row['refseq_ids'],
                variation_ids=row['variation_ids'],
                meanProb=row['meanProb'],
                stdProb=row['standardDev'],
                pred_label=row['Pred_label']
            ))

        # Bulk create objects in batches
        if len(objects_to_create) >= batch_size:
            with transaction.atomic():
                data.objects.bulk_create(objects_to_create)
            objects_to_create = []

    # Create any remaining objects
    if objects_to_create:
        with transaction.atomic():
            data.objects.bulk_create(objects_to_create)


def about(request):
    return render(request, 'about.html')


def disclaimer(request):
    return render(request, 'disclaimer.html')
