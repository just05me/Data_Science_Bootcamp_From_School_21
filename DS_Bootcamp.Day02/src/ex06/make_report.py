import sys
from analytics import Research, Analytics, Calculation
from config import steps, file_ext, file_name_output, report

if __name__=="__main__":
    little = sys.argv

    if len(little) != 2:
        raise ValueError("File name not provided")
    
    try:
        file_name = little[1]
    
        research = Research(file_name)
    
        data = research.file_reader()
    
        calc = Calculation(data)
    
        heads, tails = calc.counts()
    
        headf, tailf = calc.fractions(heads,tails)
    
        analytics = Analytics(data)
    
        predictions = analytics.predict_random(steps)
    
        p_heads = sum(1 for i in predictions if i == [1, 0])
        p_tails = sum(1 for i in predictions if i == [0, 1])
    
        total = heads + tails
    
        report=report.format(
            total=total,
            tail=tails,
            head=heads,
            fract1=tailf,
            fract2=headf,
            steps=steps,
            ptail=p_tails,
            phead=p_heads
        )
        print(report)
    
        analytics.save_file(report, file_name_output, file_ext)
    
        research.send_to_telegram("The report has been successfully sent")
    
    except Exception as e:
        research.send_to_telegram("The report hasnt been created")
    
        print(f"Error: {e}")