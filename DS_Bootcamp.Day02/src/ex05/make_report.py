from analytics import Research, Analytics
import config

def main():
    try:
        file_name = "data.csv"

        research = Research(file_name)
        
        data = research.file_reader()

        analysis = Analytics(data)

        head, tail = analysis.counts()
        
        fract1, fract2 = analysis.fractions(head, tail)

        predictions = analysis.predict_random(config.steps)

        phead = sum(1 for x in predictions if x == [1, 0])
        ptail = sum(1 for x in predictions if x == [0, 1])

        filled_report = config.report.format(
            all=len(data),
            tail=tail,
            head=head,
            fract1=fract1,
            fract2=fract2,
            steps=config.steps,
            ptail=ptail,
            phead=phead)

        analysis.save_file(filled_report.strip(), config.file_name_output, config.file_ext)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 