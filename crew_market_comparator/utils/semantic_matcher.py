import difflib

class SemanticMatcher:
    def unify(self, all_data):
        flat = [item for sublist in all_data for item in sublist]
        unified = []

        while flat:
            base = flat.pop(0)
            group = [base]

            flat_copy = flat[:]
            for other in flat_copy:
                ratio = difflib.SequenceMatcher(None, base["product"], other["product"]).ratio()
                if ratio > 0.7:
                    group.append(other)
                    flat.remove(other)

            unified.append({
                "product": base["product"],
                "entries": group,
                "confidence": round(sum(difflib.SequenceMatcher(None, base["product"], g["product"]).ratio() for g in group) / len(group), 2)
            })

        return unified
