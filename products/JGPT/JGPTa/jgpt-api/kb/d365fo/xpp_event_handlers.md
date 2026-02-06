# X++ Event Handlers

## Form control event example
```xpp
[FormControlEventHandler(formControlStr(MyForm, MyButton), FormControlEventType::Clicked)]
public static void MyButton_OnClicked(FormControl sender, FormControlEventArgs e)
{
    info("Clicked");
}
```

## Table event example
```xpp
[DataEventHandler(tableStr(SalesTable), DataEventType::ValidatedWrite)]
public static void SalesTable_onValidatedWrite(Common sender, DataEventArgs e)
{
    SalesTable st = sender as SalesTable;
    // validation
}
```

## Common mistakes
- Using overlayering patterns (avoid)
- Putting heavy logic in UI events (move to services/classes)
